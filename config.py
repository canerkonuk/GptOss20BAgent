# config.py
# Configuration file for GPT-OSS-20B Agent (optimized for stable conversation)

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
SRC_DIR = BASE_DIR / "src"

# Model file
MODEL_NAME = "gpt-oss-20b-Q5_K_M.gguf"  # change if needed
MODEL_PATH = MODELS_DIR / MODEL_NAME

# ----------------------
# LLM Settings (GPT-OSS-20B)
# ----------------------
LLM_CONFIG = {
    "n_ctx": 4092,             # context window (reduce for stability)
    "n_batch": 256,            # batch size
    "temperature": 0.7,        # lower = more deterministic
    "top_p": 0.9,              # nucleus sampling
    "top_k": 40,               # top-k sampling
    "max_tokens": 512,         # max output tokens
    "repeat_penalty": 1.15,    # reduce repetition
    "verbose": False,
    "n_threads": 8,            # CPU threads (adjust to your machine)
    "n_gpu_layers": 40      # offload layers to GPU if available (Added for google colab t4 gpu)
}

# ----------------------
# Gradio UI
# ----------------------
GRADIO_CONFIG = {
    "share": True, # For google colab test, I need public link.
    "server_name": "0.0.0.0",
    "server_port": 7860,
}

# ----------------------
# Search
# ----------------------
SEARCH_CONFIG = {
    "max_results": 10,
    "region": "wt-wt",
    "safesearch": "moderate",
    "timeout": 10,
}

# ----------------------
# Scraper
# ----------------------
SCRAPER_CONFIG = {
    "timeout": 15,
    "max_content_length": 5000,
    "head_chars": 3000,
    "tail_chars": 2000,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    },
}

# ----------------------
# System prompts (short, direct, avoids meta-reasoning)
# ----------------------
SYSTEM_PROMPTS = {
    "conversation": (
        "You are a helpful AI assistant. Answer user questions directly, clearly, and concisely. "
        "Do not explain your reasoning or your actions. Focus on providing the answer."
    ),
    "search": (
        "You are a search assistant. Summarize the search results accurately and concisely. "
        "Do not include internal reasoning or planning."
    ),
    "scrape": (
        "You are a data extraction assistant. Extract relevant information clearly and concisely. "
        "Do not provide reasoning or commentary."
    ),
}

# ----------------------
# Helper functions
# ----------------------
def validate_model_path():
    if not MODEL_PATH.exists():
        return False, f"Model not found at: {MODEL_PATH}"
    return True, "Model found"

def get_model_info():
    if MODEL_PATH.exists():
        size_mb = MODEL_PATH.stat().st_size / (1024 * 1024)
        return {
            "path": str(MODEL_PATH),
            "size_mb": round(size_mb, 2),
            "exists": True
        }
    return {
        "path": str(MODEL_PATH),
        "size_mb": 0,
        "exists": False
    }
