"""
Utility functions for the Equity Research Agent system.
"""

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from config import (
    LLM_MODEL,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    OLLAMA_MODEL,
    OLLAMA_TEMPERATURE
)


def get_llm():
    """
    Factory function to get the appropriate LLM based on configuration.

    Returns:
        ChatOllama or ChatOpenAI: Configured LLM instance

    Raises:
        ValueError: If LLM_MODEL is not 'ollama' or 'openai'
    """
    if LLM_MODEL == 'ollama':
        return ChatOllama(
            model=OLLAMA_MODEL,
            temperature=OLLAMA_TEMPERATURE
        )
    elif LLM_MODEL == 'openai':
        return ChatOpenAI(
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE
        )
    else:
        raise ValueError(
            f"Invalid LLM_MODEL: {LLM_MODEL}. Must be 'ollama' or 'openai'"
        )
