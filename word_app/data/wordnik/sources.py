from dataclasses import dataclass


@dataclass
class WordnikSourceDictionary:
    api_value: str
    title: str


AmericanHeritage = WordnikSourceDictionary(
    api_value="ahd-5",
    title=(
        "The American Heritage® Dictionary of the English Language, 5th Edition"
    ),
)
