"""Task components"""

import inspect
from typing import get_type_hints, Any

from pydantic import BaseModel, Field

from ..domain.models import SupportedTask


class FunctionSignature(BaseModel):
    name: str
    args: list[str]
    types: dict[str, str]
    return_type: str = None
    doc: str = None
    required_args: list[str] = Field(default_factory=list)
    optional_args: list[str] = Field(default_factory=list)

function_registry: dict[str, FunctionSignature] = {}

def type_to_string(type_hint) -> str:
    """Convert type hints to string representation"""
    if hasattr(type_hint, '__name__'):
        return type_hint.__name__
    else:
        return str(type_hint)


def register_function(func):
    """Decorator to automatically register function metadata"""
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)

    required_args = []
    optional_args = []
    args = []
    types = {}

    for name, param in sig.parameters.items():
        args.append(name)
        types[name] = type_to_string(type_hints.get(name, Any))

        if param.default == inspect.Parameter.empty:
            required_args.append(name)
        else:
            optional_args.append(name)

    return_type = type_to_string(type_hints.get('return', type(None)))

    signature = FunctionSignature(
        name=func.__name__,
        args=args,
        types=types,
        return_type=return_type,
        doc=func.__doc__,
        required_args=required_args,
        optional_args=optional_args
    )

    function_registry[func.__name__] = signature

    return func

@register_function
def upload_to_notion():
    raise NotImplementedError


@register_function
def send_email():
    raise NotImplementedError

@register_function
def scrape():
    raise NotImplementedError

@register_function
def planning():
    raise NotImplementedError

@register_function
def analyse():
    raise NotImplementedError


# mapping for setting component graphs to supported tasks.
AOTASK_EXECUTION_GRAPH = {
    SupportedTask.RESEARCH: [
        analyse,
        scrape,
        upload_to_notion,
    ],
    SupportedTask.PLANNING: [
        planning,
        send_email,
    ],
}


def get_task_graph(supported_task: SupportedTask):
    return AOTASK_EXECUTION_GRAPH[supported_task]