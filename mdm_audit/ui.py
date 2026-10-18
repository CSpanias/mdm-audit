"""
Shared Rich console configuration for the MDM Audit application.
"""

from rich.console import Console
from rich.theme import Theme

theme = Theme(
    {
        "success": "green",
        "error": "red",
        "warning": "yellow",
        "info": "cyan",
        "question": "bold cyan",
        "good": "green",
        "bad": "red",
        "heading": "bold white",
    }
)

console = Console(theme=theme)