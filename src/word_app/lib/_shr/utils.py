def make_value_error(name: str, value: str) -> None:
    """Helper to raise an error for some validation issue."""
    raise ValueError(
        f"Invalid value of '{value} for Datamuse configration '{name}'."
    )
