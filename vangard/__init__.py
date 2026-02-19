"""
Vangard Script Utils - A command-line interface for DAZ Studio automation.
"""

__version__ = "0.1.0"
__author__ = "Vangard Team"
__license__ = "MIT"

# Make key classes available at package level
from vangard.commands.BaseCommand import BaseCommand

__all__ = ["BaseCommand", "__version__"]
