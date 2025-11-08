"""MCP servers for AOAgent."""

from .weather import weather_mcp
from .train import train_mcp

__all__ = ["weather_mcp", "train_mcp"]