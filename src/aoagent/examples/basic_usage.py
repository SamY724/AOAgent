"""Example usage of setting up a new agent."""

from ..utils.settings import set_env_vars
from ..domain.agent import AOAgent


def craft_agent():
    set_env_vars()

    new_agent = AOAgent(
        model="claude-sonnet-4-0", provider="anthropic", instructions="Be friendly"
    )

    return new_agent


if __name__ == "__main__":
    agent = craft_agent()
    print(agent.run_sync("Hello"))
