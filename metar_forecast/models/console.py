from rich.console import Console
from rich.theme import Theme

_custom_theme = Theme(
    {
        "info": "white",
        "warning": "rgb(175,175,0)",
        "danger": "bold rgb(175,0,0)",
        "success": "green",
        "repr.number": "not bold",
    }
)

console = Console(width=100, theme=_custom_theme)
