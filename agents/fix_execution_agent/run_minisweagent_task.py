import subprocess
import sys
import os
import json
import re

def ensure_directories(agent_test_path, backup_agent_path):
    os.makedirs(agent_test_path, exist_ok=True)
    os.makedirs(backup_agent_path, exist_ok=True)

def install_python_package(project_root):
    """Install the project in editable mode if not already installed.

    Attempts to infer the package name from pyproject.toml or setup.py and
    uses `pip show` to check whether it's already installed. If the name
    cannot be determined we fall back to installing when setup.py or
    pyproject.toml exists.
    """
    setup_py = os.path.join(project_root, "setup.py")
    pyproject_toml = os.path.join(project_root, "pyproject.toml")

    def _infer_name():
        # Try pyproject.toml first
        if os.path.exists(pyproject_toml):
            try:
                # Python 3.11+ has tomllib
                import tomllib
                with open(pyproject_toml, "rb") as f:
                    data = tomllib.load(f)
                # poetry or PEP 621
                if isinstance(data, dict):
                    if "project" in data and isinstance(data["project"], dict):
                        name = data["project"].get("name")
                        if name:
                            return name
                    tool = data.get("tool")
                    if isinstance(tool, dict):
                        poetry = tool.get("poetry")
                        if isinstance(poetry, dict):
                            name = poetry.get("name")
                            if name:
                                return name
            except Exception:
                # fallback to a cheap regex parse if tomllib not available or parsing fails
                try:
                    with open(pyproject_toml, "r", encoding="utf-8") as f:
                        txt = f.read()
                    m = re.search(r"name\s*=\s*[\"']([^\"']+)[\"']", txt)
                    if m:
                        return m.group(1)
                except Exception:
                    pass

        # Try setup.py
        if os.path.exists(setup_py):
            try:
                with open(setup_py, "r", encoding="utf-8") as f:
                    txt = f.read()
                m = re.search(r"name\s*=\s*[\"']([^\"']+)[\"']", txt)
                if m:
                    return m.group(1)
            except Exception:
                pass

        return None

    if not (os.path.exists(setup_py) or os.path.exists(pyproject_toml)):
        return

    pkg_name = _infer_name()
    if pkg_name:
        # Check if package is installed
        try:
            res = subprocess.run([sys.executable, "-m", "pip", "show", pkg_name], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            if res.returncode == 0 and res.stdout:
                print(f"Package '{pkg_name}' already installed; skipping install.")
                return
        except Exception:
            # If pip show fails for some reason, fall back to installing
            pass

    # Fall back to installing editable package
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", project_root], check=True)

def generate_file_tree(project_root, max_depth=2):
    """Generate a file tree structure using Python (cross-platform compatible)."""
    def _generate_tree(path, prefix="", depth=0, is_last=True):
        if depth > max_depth:
            return []
        
        lines = []
        # Get the name to display
        name = os.path.basename(path) if path != project_root else os.path.basename(project_root) or project_root
        
        # Add current item
        if path != project_root:
            connector = "└── " if is_last else "├── "
            lines.append(prefix + connector + name)
            new_prefix = prefix + ("    " if is_last else "│   ")
        else:
            lines.append(name)
            new_prefix = prefix
        
        # Add children if directory and not at max depth
        if depth < max_depth and os.path.isdir(path):
            try:
                entries = sorted(os.listdir(path))
                # Filter out hidden files/directories (starting with .)
                entries = [e for e in entries if not e.startswith('.')]
                
                for i, entry in enumerate(entries):
                    entry_path = os.path.join(path, entry)
                    is_last_entry = (i == len(entries) - 1)
                    lines.extend(_generate_tree(entry_path, new_prefix, depth + 1, is_last_entry))
            except PermissionError:
                pass
        
        return lines
    
    tree_lines = _generate_tree(project_root)
    tree_output = "\n".join(tree_lines)
    
    tree_file_path = os.path.join(project_root, "file_tree.txt")
    with open(tree_file_path, "w", encoding="utf-8") as tree_file:
        tree_file.write(tree_output)
    return tree_output

def run_pytest_if_available(project_root):
    """Run pytest if available, otherwise skip with a message."""
    try:
        # Check if pytest is available
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            subprocess.run([sys.executable, "-m", "pytest", "--cov", project_root], cwd=project_root)
        else:
            print("pytest not available, skipping tests.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("pytest not available, skipping tests.")

def main():
    # Set UTF-8 encoding for Windows compatibility
    if sys.platform == "win32":
        os.environ["PYTHONIOENCODING"] = "utf-8"
        os.environ["FIXCODE_SILENT_STARTUP"] = "1"  # Suppress emoji output that causes encoding issues
    
    # Read important info from JSON
    with open("agent_task_info.json", "r", encoding="utf-8") as f:
        info = json.load(f)
    project_root = info["project_root"]
    agent_test_path = info["agent_test_path"]
    backup_agent_path = info["backup_agent_path"]
    task = (
        f"{info['task']}. The problem is in the file: {info['problem_file']}"
    )

    install_python_package(project_root)
    ensure_directories(agent_test_path, backup_agent_path)

    # Generate file tree and include it in the task
    tree_output = generate_file_tree(project_root)
    print("File tree:")
    print(tree_output)

    # Run all tests before fix and show coverage
    print("Running all tests BEFORE fix (baseline)...")
    run_pytest_if_available(project_root)

    os.environ["AGENT_TEST_PATH"] = agent_test_path
    os.environ["BACKUP_AGENT_PATH"] = backup_agent_path
    import time
    start_time = time.time()
    
    # Prepare environment for subprocess with UTF-8 encoding
    env = os.environ.copy()
    if sys.platform == "win32":
        env["PYTHONIOENCODING"] = "utf-8"
        env["FIXCODE_SILENT_STARTUP"] = "1"
    
    # Use --yolo and --exit-immediately to avoid interactive prompts
    # Don't redirect stdout/stderr to avoid prompt_toolkit console issues on Windows
    process = subprocess.Popen(
        [sys.executable, "-m", "src.fixcodeagent", "--task", f"{task}\n\n{tree_output}", "--yolo", "--exit-immediately"],
        env=env
    )
    try:
        process.wait()  # Wait for process to complete
    except KeyboardInterrupt:
        process.terminate()
        print("\nProcess terminated by user.")
    end_time = time.time()
    print(f"\nAgent finished in {end_time - start_time:.2f} seconds.")

    # Run all tests after fix and show coverage
    print("Running all tests AFTER fix...")
    run_pytest_if_available(project_root)

if __name__ == "__main__":
    main()