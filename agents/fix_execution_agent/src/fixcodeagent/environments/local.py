import base64
import os
import platform
import subprocess
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class LocalEnvironmentConfig:
    cwd: str = ""
    env: dict[str, str] = field(default_factory=dict)
    timeout: int = 30


class LocalEnvironment:
    def __init__(self, *, config_class: type = LocalEnvironmentConfig, **kwargs):
        """This class executes PowerShell commands directly on the local machine."""
        self.config = config_class(**kwargs)

    def execute(self, command: str, cwd: str = "", *, timeout: int | None = None):
        """Execute a command in the local environment and return the result as a dict."""
        cwd = cwd or self.config.cwd or os.getcwd()
        # Use PowerShell on Windows
        if platform.system() == "Windows":
            # Use -EncodedCommand for reliable Unicode support (especially for Chinese characters)
            # PowerShell's -EncodedCommand expects a Base64-encoded UTF-16LE string
            # Set console encoding and ensure plain text output (not CLIXML)
            # Wrap command to suppress CLIXML and ensure UTF-8 encoding
            # Set ErrorView to NormalView to prevent CLIXML serialization
            full_command = (
                "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
                "[Console]::InputEncoding = [System.Text.Encoding]::UTF8; "
                "$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'; "
                "$OutputEncoding = [System.Text.Encoding]::UTF8; "
                "$ErrorView = 'NormalView'; "
                "$ErrorActionPreference = 'Continue'; "
                "try { "
                f"  {command} 2>&1 "
                "} catch { "
                "  Write-Host $_.Exception.Message; "
                "  exit 1 "
                "}"
            )
            # Encode the command as UTF-16LE (little-endian), then Base64 encode it
            encoded_command = base64.b64encode(full_command.encode('utf-16-le')).decode('ascii')
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-OutputFormat", "Text", "-EncodedCommand", encoded_command],
                text=True,
                cwd=cwd,
                env={**os.environ, **self.config.env, "PYTHONIOENCODING": "utf-8"},
                timeout=timeout or self.config.timeout,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        else:
            # Fallback to shell=True for non-Windows systems
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                cwd=cwd,
                env=os.environ | self.config.env,
                timeout=timeout or self.config.timeout,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        return {"output": result.stdout, "returncode": result.returncode}

    def get_template_vars(self) -> dict[str, Any]:
        return asdict(self.config) | platform.uname()._asdict() | os.environ
