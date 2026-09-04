"""Local compatibility layer for the retired Emergent LLM integration."""

import os

# server.py reads this legacy variable during import. Populate it from the
# supported OpenAI configuration so existing API startup remains compatible.
os.environ.setdefault("EMERGENT_LLM_KEY", os.getenv("OPENAI_API_KEY", ""))
