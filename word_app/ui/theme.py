# Change variables in /word-app/word_app/app/main.css when doing updates.
from textual.theme import Theme

DarkTheme = Theme(
    name="Dark Theme",
    primary="#D8D8D8",
    secondary="#E0E0E0",
    accent="#FFA62B",
    warning="#FFA62B",
    error="#BA3C5B",
    success="#4EBF71",
    foreground="#E0E0E0",
    variables={
        "footer-key-foreground": "#3376CD",
        "user-action": "#3376CD",
        "user-hover": "#FFA62B",
    },
)

LightTheme = Theme(
    name="Light Theme",
    primary="#1E1E1E",
    secondary="#121212",
    accent="#FFA62B",
    warning="#FFA62B",
    error="#BA3C5B",
    success="#4EBF71",
    surface="#D8D8D8",
    panel="#D0D0D0",
    background="#E0E0E0",
    foreground="#121212",
    dark=False,
    variables={
        "footer-key-foreground": "#3376CD",
        "user-action": "#3376CD",
        "user-hover": "#FFA62B",
    },
)
