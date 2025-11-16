#!/usr/bin/env python3

"""Run fix-code-agent in your local environment. This is the default executable `fix-code`."""
# Read this first: https://fix-code-agent.com/latest/usage/mini/  (usage)

import os
import traceback
from pathlib import Path
from typing import Any

import typer
import yaml
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import PromptSession
from rich.console import Console

from fixcodeagent import global_config_dir
from fixcodeagent.agents.interactive import InteractiveAgent
from fixcodeagent.agents.interactive_textual import TextualAgent
from fixcodeagent.config import builtin_config_dir, get_config_path
from fixcodeagent.environments.local import LocalEnvironment
from fixcodeagent.models import get_model
from fixcodeagent.run.extra.config import configure_if_first_time
from fixcodeagent.run.utils.save import save_traj
from fixcodeagent.utils.log import logger

DEFAULT_CONFIG = Path(os.getenv("FIXCODE_MINI_CONFIG_PATH", builtin_config_dir / "mini.yaml"))
DEFAULT_OUTPUT = global_config_dir / "last_mini_run.traj.json"
console = Console(highlight=False)
app = typer.Typer(rich_markup_mode="rich")
prompt_session = PromptSession(history=FileHistory(global_config_dir / "mini_task_history.txt"))
_HELP_TEXT = """Run fix-code-agent in your local environment.

[not dim]
There are two different user interfaces:

[bold green]fix-code[/bold green] Simple REPL-style interface
[bold green]fix-code -v[/bold green] Pager-style interface (Textual)

More information about the usage: [bold green]https://fix-code-agent.com/latest/usage/mini/[/bold green]
[/not dim]
"""


# fmt: off
@app.command(help=_HELP_TEXT)
def main(
    visual: bool = typer.Option(False, "-v", "--visual", help="Toggle (pager-style) UI (Textual) depending on the FIXCODE_VISUAL_MODE_DEFAULT environment setting",),
    model_name: str | None = typer.Option( None, "-m", "--model", help="Model to use",),
    model_class: str | None = typer.Option(None, "--model-class", help="Model class to use (e.g., 'anthropic' or 'fixcodeagent.models.anthropic.AnthropicModel')", rich_help_panel="Advanced"),
    task: str | None = typer.Option(None, "-t", "--task", help="Task/problem statement", show_default=False),
    yolo: bool = typer.Option(False, "-y", "--yolo", help="Run without confirmation"),
    cost_limit: float | None = typer.Option(None, "-l", "--cost-limit", help="Cost limit. Set to 0 to disable."),
    config_spec: Path = typer.Option(DEFAULT_CONFIG, "-c", "--config", help="Path to config file"),
    output: Path | None = typer.Option(DEFAULT_OUTPUT, "-o", "--output", help="Output trajectory file"),
    exit_immediately: bool = typer.Option( False, "--exit-immediately", help="Exit immediately when the agent wants to finish instead of prompting.", rich_help_panel="Advanced"),
) -> Any:
    # fmt: on
    configure_if_first_time()
    config_path = get_config_path(config_spec)
    console.print(f"Loading agent config from [bold green]'{config_path}'[/bold green]")
    # Read the config file using UTF-8 by default. On Windows Path.read_text()
    # uses the locale encoding (cp936 / gbk here) which can fail for UTF-8 files.
    # Try sensible fallbacks so this works regardless of file BOM or system locale.
    try:
        text = config_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            # Some files include a UTF-8 BOM
            text = config_path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            # Fall back to the system locale but don't crash; replace undecodable
            # bytes so the YAML loader can still run and provide a helpful error.
            text = config_path.read_text(encoding="cp936", errors="replace")

    config = yaml.safe_load(text)

    if not task:
        console.print("[bold yellow]What do you want to do?")
        task = prompt_session.prompt(
            "",
            multiline=True,
            bottom_toolbar=HTML(
                "Submit task: <b fg='yellow' bg='black'>Esc+Enter</b> | "
                "Navigate history: <b fg='yellow' bg='black'>Arrow Up/Down</b> | "
                "Search history: <b fg='yellow' bg='black'>Ctrl+R</b>"
            ),
        )
        console.print("[bold green]Got that, thanks![/bold green]")

    if yolo:
        config.setdefault("agent", {})["mode"] = "yolo"
    if cost_limit:
        config.setdefault("agent", {})["cost_limit"] = cost_limit
    if exit_immediately:
        config.setdefault("agent", {})["confirm_exit"] = False
    if model_class is not None:
        config.setdefault("model", {})["model_class"] = model_class
    model = get_model(model_name, config.get("model", {}))
    env = LocalEnvironment(**config.get("env", {}))

    # Both visual flag and the FIXCODE_VISUAL_MODE_DEFAULT flip the mode, so it's essentially a XOR
    agent_class = InteractiveAgent
    if visual == (os.getenv("FIXCODE_VISUAL_MODE_DEFAULT", "false") == "false"):
        agent_class = TextualAgent

    agent = agent_class(model, env, **config.get("agent", {}))
    exit_status, result, extra_info = None, None, None
    try:
        exit_status, result = agent.run(task)  # type: ignore[arg-type]
    except Exception as e:
        logger.error(f"Error running agent: {e}", exc_info=True)
        exit_status, result = type(e).__name__, str(e)
        extra_info = {"traceback": traceback.format_exc()}
    finally:
        if output:
            save_traj(agent, output, exit_status=exit_status, result=result, extra_info=extra_info)  # type: ignore[arg-type]
    return agent


if __name__ == "__main__":
    app()
