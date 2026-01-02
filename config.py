"""
Configuration file for the Equity Research Agent system.

Switch between 'ollama' (local, requires ~2-7GB storage) and 'openai' (API-based, no storage).
"""

# LLM Model Selection
# Options: 'ollama' or 'openai'
# Note: 'ollama' requires local model download (~2-7GB)
# 'openai' requires API key in environment variable OPENAI_API_KEY
LLM_MODEL = 'ollama'

# OpenAI Configuration
OPENAI_MODEL = 'gpt-4o-mini'
OPENAI_TEMPERATURE = 0

# Ollama Configuration
OLLAMA_MODEL = 'llama3.2'
OLLAMA_TEMPERATURE = 0
