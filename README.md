# GptOss20BAgent

A multi-mode AI agent powered by GPT-OSS-20B model with web search and scraping capabilities.

## Features

- **💬 Conversation Mode**: Chat with the AI assistant
- **🔍 Search Mode**: Search the web using DuckDuckGo and get AI-processed results
- **🌐 Scrape Mode**: Extract and analyze content from web pages

## Tech Stack

- **Model**: gpt-oss-20b-Q5_K_M.gguf (20B parameters, Q5 quantization)
- **LLM Framework**: llama-cpp-python
- **UI**: Gradio
- **Search**: DuckDuckGo Search (free, no API key required)
- **Scraping**: BeautifulSoup4

## System Requirements

- **RAM**: 16GB minimum, 32GB recommended
- **CPU**: Multi-core processor (8 cores recommended)
- **Storage**: ~15GB for model file
- **Python**: 3.8 or higher

## Installation

### 1. Clone or Download the Project

```bash
cd GptOss20BAgent
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** Installing `llama-cpp-python` may take a few minutes as it compiles C++ code.

### 4. Download the Model

1. Download `gpt-oss-20b-Q5_K_M.gguf` from:
   - https://huggingface.co/unsloth/gpt-oss-20b-GGUF

2. Place the file in the `models/` directory:
   ```
   GptOss20BAgent/
   └── models/
       └── gpt-oss-20b-Q5_K_M.gguf
   ```

## Usage

### Run the Application

```bash
python main.py
```

The application will:
1. Check for the model file
2. Load the model (takes ~1 minute)
3. Launch Gradio interface
4. Open in your default browser

Access the interface at: `http://localhost:7860`

### Using Different Modes

#### Conversation Mode
- Simple chat interface
- Ask questions, get code help, discuss topics
- Maintains conversation history

#### Search Mode
- Enter search queries
- Get AI-summarized search results from DuckDuckGo
- Combines multiple sources

#### Scrape Mode
- Enter any URL to scrape
- Optionally ask specific questions about the content
- AI extracts and analyzes the information

## Configuration

Edit `config.py` to customize:

- **Model settings**: Context window, temperature, tokens, etc.
- **Server settings**: Port, host, sharing options
- **Search settings**: Number of results, region, safe search
- **Scraper settings**: Timeout, content length limits

## Project Structure

```
GptOss20BAgent/
├── models/                  # Model files (gitignored)
├── src/
│   ├── agent.py            # LLM logic
│   ├── search.py           # DuckDuckGo search
│   ├── scraper.py          # Web scraping
│   └── ui.py               # Gradio interface
├── venv/                   # Virtual environment (gitignored)
├── config.py               # Configuration
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── instructions.md         # Developer documentation
└── README.md               # This file
```

## Troubleshooting

### Model Not Loading
- **Issue**: Out of memory error
- **Solution**: Close other applications, ensure you have 16GB+ RAM

### Slow Response Times
- **Issue**: Responses take a long time
- **Solution**: This is expected on CPU. 20B models generate ~1-5 tokens/sec on CPU.

### Import Errors
- **Issue**: Module not found errors
- **Solution**: Make sure virtual environment is activated and dependencies are installed

### Connection Refused
- **Issue**: Can't access http://localhost:7860
- **Solution**: Check if port 7860 is available. Change port in `config.py` if needed.

## Performance Notes

- **First response**: May be slower due to prompt processing
- **Subsequent responses**: Faster as context is cached
- **CPU vs GPU**: This project uses CPU inference. For faster responses, consider GPU-enabled builds of llama-cpp-python

## Future Enhancements

- Add conversation export/import
- Support for more search engines
- Advanced scraping options (JavaScript rendering)
- Custom React frontend
- RAG (Retrieval Augmented Generation) support
- Multi-document analysis

## License

This is a learning project. The model (GPT-OSS-20B) has its own license on HuggingFace.

## Credits

- **Model**: GPT-OSS-20B by Unsloth
- **Framework**: llama-cpp-python by Andrei Betlen
- **UI**: Gradio
- **Search**: duckduckgo-search
- **Scraping**: BeautifulSoup4

## Support

For issues or questions:
1. Check `instructions.md` for developer context
2. Review configuration in `config.py`
3. Check console output for error messages

---
