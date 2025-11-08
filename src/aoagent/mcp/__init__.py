"""MCP servers for AOAgent."""

from .weather import mcp as weather_mcp
from .train import mcp as train_mcp

__all__ = ["weather_mcp", "train_mcp"]