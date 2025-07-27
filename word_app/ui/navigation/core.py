from dataclasses import dataclass


@dataclass
class Navigateable:
    action: str
    id: str
    name: str
    description: str
    kb_binding: str

    @property
    def callable_str(self) -> str:
        return self.action

    @property
    def binding(self) -> tuple[str, str, str]:
        return self.kb_binding, self.callable_str, self.name
