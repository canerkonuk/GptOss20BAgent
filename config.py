"""
Configuration file for GPT-OSS-20B Agent
All settings and paths are defined here
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
SRC_DIR = BASE_DIR / "src"

# Model configuration
# Change this to match your model file name
# Common options: gpt-oss-20b-Q4_K_M.gguf, gpt-oss-20b-Q5_K_M.gguf, gpt-oss-20b-Q8_0.gguf
MODEL_NAME = "gpt-oss-20b-Q5_K_M.gguf"
MODEL_PATH = MODELS_DIR / MODEL_NAME

# LLM Settings
# These settings are optimized based on Google Colab testing with T4 GPU
# For cloud CPU (8 vCPU, 32GB RAM), using n_threads=8
LLM_CONFIG = {
    "n_ctx": 2048,              # Context window size (reduced for better performance)
    "n_threads": 8,             # Use all 8 vCPU threads (cloud computer)
    "n_batch": 256,             # Batch size for prompt processing
    "temperature": 0.2,         # Response randomness - lower = more focused/deterministic
    "top_p": 0.8,               # Nucleus sampling
    "top_k": 30,                # Top-k sampling
    "max_tokens": 512,          # Max tokens in response
    "repeat_penalty": 1.2,      # Penalize repetition (higher = less repetition)
    "verbose": False,           # Disable llama.cpp logs
}

# Gradio UI Settings
GRADIO_CONFIG = {
    "share": False,             # Set True to create public link
    "server_name": "0.0.0.0",   # Listen on all interfaces
    "server_port": 7860,        # Port number
}

# Search Settings
# Token usage: ~10 results × 300 chars/result = ~3,000 chars ≈ 750 tokens
# Well within the available ~1,236 token budget for context
SEARCH_CONFIG = {
    "max_results": 10,          # Number of search results to fetch (safe for 2048 ctx)
    "region": "wt-wt",          # Region (wt-wt = worldwide)
    "safesearch": "moderate",   # Safe search level
    "timeout": 10,              # Request timeout in seconds
}

# Scraper Settings
# Token Budget Strategy for n_ctx=2048:
#   System prompt: ~50 tokens
#   User question: ~50 tokens
#   Conversation history: ~200 tokens
#   AI response (max_tokens): 512 tokens
#   Available for scraped content: ~1,236 tokens ≈ 5,000 chars
SCRAPER_CONFIG = {
    "timeout": 15,              # Request timeout in seconds
    "max_content_length": 5000,  # Max chars (~1,250 tokens) - safe for 2048 ctx
    "head_chars": 3000,         # First N chars to keep when truncating
    "tail_chars": 2000,         # Last N chars to keep when truncating
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
}

# System prompts for different modes
SYSTEM_PROMPTS = {
    "conversation": (
        "You are a helpful AI assistant. Provide clear, accurate, and concise responses."
    ),
    "search": (
        "You are a search assistant. Analyze the search results and provide a comprehensive summary."
    ),
    "scrape": (
        "You are a data extraction assistant. Extract and present the relevant information clearly."
    ),
}

def validate_model_path():
    """Check if model file exists"""
    if not MODEL_PATH.exists():
        return False, f"Model not found at: {MODEL_PATH}"
    return True, "Model found"

def get_model_info():
    """Get model file information"""
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
