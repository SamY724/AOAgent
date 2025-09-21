"""Module containing the domain logic for aoagent archetype"""

from typing import Optional
import yaml

from pydantic_ai import Agent

from ..utils.settings import CONFIG_DIR

with open(CONFIG_DIR / "available_models.yml", "r") as config_file:
    incorporated_model_index = yaml.safe_load(config_file)


def _check_model_is_incorporated(model: str, provider: str) -> bool:
    for models in incorporated_model_index[provider]:
        if model in models:
            return True

    return False


class AOAgent(Agent):
    def __init__(
        self, model: str, provider: str, instructions: Optional[str] = None
    ) -> None:
        is_available = _check_model_is_incorporated(model, provider)

        if is_available:
            self.model = f"{provider}:{model}"

        if instructions:
            self.instructions = instructions

        super().__init__(self.model)
