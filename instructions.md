# GPT-OSS-20B Agent - Project Instructions

## Project Overview

This is an AI agent project built for learning purposes. The agent has three operational modes:
1. **Conversation Mode** - Standard chat with the LLM
2. **Search Mode** - Search the web and process results
3. **Scrape Mode** - Scrape web pages and extract data

## Technical Stack Decisions

### Core Components
- **Language**: Python
- **LLM Framework**: llama-cpp-python (https://github.com/abetlen/llama-cpp-python)
- **Model**: gpt-oss-20b-Q5_K_M.gguf from https://huggingface.co/unsloth/gpt-oss-20b-GGUF
- **UI Framework**: Gradio (simple interface for learning)
- **Search**: DuckDuckGo Search (free, no API key needed)
- **Web Scraping**: BeautifulSoup4 (simple and reliable)

### Why These Choices?
- **llama-cpp-python**: Mature, efficient CPU inference, supports GGUF format
- **Gradio**: Quick UI prototyping, built-in chat interface, easy to learn
- **DuckDuckGo**: Free search API, no costs, good for learning
- **BeautifulSoup**: Old, stable, simple library for HTML parsing
- **No Google Search**: Avoiding complexity and API costs for now
- **No Playwright**: Too complex for this learning project

## Infrastructure
- **Cloud Computer**: 32GB RAM, 8 vCPU
- **Model Size**: ~13-15GB RAM usage (Q5_K_M quantization)
- **Expected Speed**: 1-5 tokens/sec on CPU

## Project Structure

```
GPT-OSS-20B-Agent/
├── venv/                           # Virtual environment (gitignored)
├── models/                         # Model files (gitignored)
│   └── gpt-oss-20b-Q5_K_M.gguf    # Add this file before running
├── src/
│   ├── agent.py                    # Main AI agent logic with llama-cpp-python
│   ├── search.py                   # DuckDuckGo search functionality
│   ├── scraper.py                  # BeautifulSoup web scraping
│   └── ui.py                       # Gradio interface (3 tabs)
├── requirements.txt                # Python dependencies
├── config.py                       # Configuration (model path, settings)
├── main.py                         # Entry point to run the application
├── README.md                       # User-facing setup instructions
├── instructions.md                 # This file - developer context
└── .gitignore                      # Ignore venv, models, cache
```

## Setup Steps (For Cloud Computer)

1. **Clone/Upload Project** to cloud computer
2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Download Model**: Place `gpt-oss-20b-Q5_K_M.gguf` in `models/` folder
5. **Run Application**:
   ```bash
   python main.py
   ```

## Development Notes

- Everything is self-contained in the project directory via venv
- Model file is NOT included in git (too large)
- Code is designed to handle missing model gracefully with clear error messages
- Focus is on learning the process, not production-ready code
- Future enhancement: Could replace Gradio with React frontend

## Token Budget Strategy (n_ctx = 2048)

**Critical**: With `n_ctx=2048`, we must carefully manage token usage to avoid overflow errors.

### Token Allocation Breakdown:
```
Total context window: 2048 tokens
├─ System prompt:         ~50 tokens
├─ User question:         ~50 tokens
├─ Conversation history:  ~200 tokens (last 6 messages)
├─ AI response:           512 tokens (max_tokens)
└─ Available for context: ~1,236 tokens
```

### Implementation Strategies:

#### 1. Conversation Mode
- Keeps only **last 6 messages** (3 exchanges) in history
- Prevents unbounded history growth
- ~200 token budget for history

#### 2. Search Mode
- Limits to **10 search results** via `SEARCH_CONFIG`
- Each result: ~300 chars (title + URL + description)
- Total: ~3,000 chars ≈ **750 tokens** ✅ Safe
- Well within 1,236 token budget

#### 3. Scrape Mode (Head+Tail Strategy)
- **Problem**: Web pages can be 50k-500k+ characters
- **Solution**: Intelligent truncation with head+tail preservation
- `max_content_length`: 5,000 chars (~1,250 tokens) ✅ Safe
- When content exceeds limit:
  - Takes **first 3,000 chars** (beginning of page)
  - Takes **last 2,000 chars** (end of page)
  - Adds separator: `[Content truncated - showing first X and last Y chars]`
- **Why head+tail?** Preserves introduction AND conclusion context
- **Extensible**: Can later add chunking or summarization pipelines

### Future Improvements:
- Add actual token counting (tiktoken or similar)
- Implement recursive summarization for large documents
- Batch processing for multiple pages
- Dynamic context allocation based on mode

## Key Features to Implement

### 1. Conversation Mode
- Load model using llama-cpp-python
- Maintain conversation history
- Stream responses to Gradio UI

### 2. Search Mode
- Accept search query from user
- Call DuckDuckGo API
- Pass results to LLM for processing/summarization
- Display formatted results

### 3. Scrape Mode
- Accept URL from user
- Fetch page with requests
- Parse HTML with BeautifulSoup
- Extract relevant content
- LLM can structure/summarize scraped data

## Next Steps After Project Creation

1. Test locally (code review)
2. Upload to cloud computer
3. Download GGUF model to `models/` folder
4. Create and activate venv
5. Install dependencies
6. Run and debug
7. Iterate and improve

## Important Reminders

- **Model path**: `models/gpt-oss-20b-Q5_K_M.gguf`
- **Always use venv**: Keep dependencies isolated
- **Check RAM usage**: Monitor when running 20B model
- **Start simple**: Get basic functionality working first
- **Gradio is temporary**: Can be replaced with better UI later

## Troubleshooting & Known Issues

### Issue 1: Model Shows Reasoning/Thinking Process
**Problem**: Model outputs internal reasoning like "So I guess...", "They want...", "Probably..." instead of direct answers.

**Cause**: Some LLMs are trained with chain-of-thought reasoning and may expose their thinking process.

**Solution**:
- Updated system prompts to explicitly instruct: "Do not show your reasoning process or thinking steps"
- Improved prompt format with clear sections: `### Instructions`, `### Current Question`, `### Response`
- Added stop sequences: `["User:", "System:", "###", "\n\n\n"]`
- These changes are in `config.py` (SYSTEM_PROMPTS) and `src/agent.py` (chat function)

**Alternative Solutions** (if issue persists):
- Lower temperature in `config.py` (e.g., from 0.7 to 0.5 for more focused responses)
- Increase `repeat_penalty` to discourage rambling
- Try different prompt formats (model-specific)

### Issue 2: DuckDuckGo Search Package Warning
**Problem**: Warning about `duckduckgo_search` being renamed to `ddgs`

**Solution**:
- Updated `requirements.txt`: Changed `duckduckgo-search` to `ddgs`
- Updated `src/search.py`: Changed import from `duckduckgo_search` to `ddgs`
- Run: `pip uninstall duckduckgo-search && pip install ddgs`

## Session Continuation

If resuming this project in a new session:
1. Read this file first
2. Review the project structure
3. Check what's already implemented
4. Continue from where development stopped
5. Refer to TODO comments in code for pending tasks

---

**Project Goal**: Learn how AI agents work by building a practical multi-mode agent system.
