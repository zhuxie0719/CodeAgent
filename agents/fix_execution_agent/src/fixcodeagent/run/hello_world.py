import os
from pathlib import Path

import typer
import yaml

from fixcodeagent import package_dir
from fixcodeagent.agents.default import DefaultAgent
from fixcodeagent.environments.local import LocalEnvironment
from fixcodeagent.models.litellm_model import LitellmModel

app = typer.Typer()


@app.command()
def main(
    task: str = typer.Option(..., "-t", "--task", help="Task/problem statement", show_default=False, prompt=True),
    model_name: str = typer.Option(
        os.getenv("FIXCODE_MODEL_NAME"),
        "-m",
        "--model",
        help="Model name (defaults to FIXCODE_MODEL_NAME env var)",
        prompt="What model do you want to use?",
    ),
) -> DefaultAgent:
    config_path = Path(package_dir / "config" / "default.yaml")
    # Read with UTF-8 encoding to handle special characters
    try:
        text = config_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            text = config_path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            text = config_path.read_text(encoding="cp936", errors="replace")
    agent = DefaultAgent(
        LitellmModel(model_name=model_name),
        LocalEnvironment(),
        **yaml.safe_load(text)["agent"],
    )
    agent.run(task)
    return agent


if __name__ == "__main__":
    app()
