from dataclasses import dataclass


@dataclass
class Navigateable:
    action: str
    kb_binding: str
    name: str

    @property
    def binding(self) -> tuple[str, str, str]:
        return self.kb_binding, self.action, self.name
