import subprocess
import sys

def main():
    task = "solve the problems on issue.txt"
    process = subprocess.Popen(
        [sys.executable, "-m", "src.minisweagent", "--task", task, "--yolo"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    try:
        for line in process.stdout:
            print(line, end='')  # Print each line as it arrives
    except KeyboardInterrupt:
        process.terminate()
        print("\nProcess terminated by user.")

if __name__ == "__main__":
    main()