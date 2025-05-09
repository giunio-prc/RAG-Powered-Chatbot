"""
Executable script for RAG Powered Chatbot.
"""

import sys
from pathlib import Path

import click
from loguru import logger

# ruff: noqa: E402
project_root = Path(__file__).parent.parent
sys.path.append((project_root).as_posix())

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # when running as a frozen executable
    running_folder = Path(sys.executable).parent
else:
    running_folder = Path(__file__).parent

from rag_powered_chatbot import (
    main as main_package
)


@click.command()
def main():
    """
    This is a script that facilitate the creation of an executable

    \b
    '''
    Another example
    '''
    NOTE: Check here.

    Other notes here
    """

    logger.info(f"This is the working location {running_folder}")
    logger.info(main_package.hello_world())

if __name__ == "__main__":
    main()
