"""
Gradio UI for the AI Agent
Provides three-tab interface: Conversation, Search, Scrape
"""

import gradio as gr
from src.agent import get_agent
from src.search import get_search_engine
from src.scraper import get_scraper
import config


def create_interface():
    """Create and return the Gradio interface"""

    agent = get_agent()
    search_engine = get_search_engine()
    web_scraper = get_scraper()

    # ===== CONVERSATION TAB =====
    def conversation_chat(message, history):
        """Handle conversation mode chat"""
        if not agent.is_ready():
            return "Error: Model not loaded. Please restart the application."

        agent.set_mode("conversation")

        # Stream response
        response = ""
        for chunk in agent.chat(message, stream=True):
            response += chunk
            yield response

    # ===== SEARCH TAB =====
    def search_and_process(query, history):
        """Handle search mode"""
        if not agent.is_ready():
            return "Error: Model not loaded. Please restart the application."

        if not query.strip():
            return "Please enter a search query."

        # Perform search
        yield "Searching DuckDuckGo..."

        success, results = search_engine.search_and_format(query)

        if not success:
            yield f"Search failed: {results}"
            return

        # Let AI process the results
        agent.set_mode("search")
        yield "Processing search results with AI..."

        context = f"Search Query: {query}\n\nSearch Results:\n{results}"

        response = "Processing search results with AI...\n\n"
        for chunk in agent.chat_with_context(
            f"Please analyze these search results for the query: '{query}'",
            context,
            stream=True
        ):
            response += chunk
            yield response

    # ===== SCRAPE TAB =====
    def scrape_and_process(url, question, history):
        """Handle scrape mode"""
        if not agent.is_ready():
            return "Error: Model not loaded. Please restart the application."

        if not url.strip():
            return "Please enter a URL to scrape."

        # Scrape the URL
        yield f"Scraping {url}..."

        success, content = web_scraper.scrape_and_format(url)

        if not success:
            yield f"Scraping failed: {content}"
            return

        # Let AI process the scraped content
        agent.set_mode("scrape")

        if question and question.strip():
            prompt = question
            response = f"Analyzing scraped content...\n\nQuestion: {question}\n\n"
        else:
            prompt = "Please summarize the key information from this web page."
            response = "Analyzing scraped content...\n\n"

        for chunk in agent.chat_with_context(prompt, content, stream=True):
            response += chunk
            yield response

    # ===== BUILD INTERFACE =====
    with gr.Blocks(title="GPT-OSS-20B Agent", theme=gr.themes.Soft()) as interface:

        gr.Markdown(
            """
            # GPT-OSS-20B Agent
            ### Multi-Mode AI Assistant: Conversation | Search | Scrape
            """
        )

        # Check if model is loaded
        model_info = config.get_model_info()
        if model_info["exists"]:
            gr.Markdown(f"**Model Status:** ✅ Loaded ({model_info['size_mb']} MB)")
        else:
            gr.Markdown(
                f"**Model Status:** ❌ Not found at `{model_info['path']}`\n\n"
                "Please add the model file before running."
            )

        with gr.Tabs():

            # === CONVERSATION TAB ===
            with gr.Tab("💬 Conversation"):
                gr.Markdown("Chat with the AI assistant in conversation mode.")

                conversation_interface = gr.ChatInterface(
                    fn=conversation_chat,
                    type="messages",
                    examples=[
                        "What is machine learning?",
                        "Explain quantum computing in simple terms",
                        "Write a Python function to calculate factorial",
                    ],
                    title="",
                    description="",
                )

            # === SEARCH TAB ===
            with gr.Tab("🔍 Search"):
                gr.Markdown(
                    "Search the web using DuckDuckGo and get AI-processed results."
                )

                search_interface = gr.ChatInterface(
                    fn=search_and_process,
                    type="messages",
                    textbox=gr.Textbox(
                        placeholder="Enter your search query...",
                        label="Search Query"
                    ),
                    examples=[
                        "Latest developments in AI",
                        "Python best practices 2025",
                        "How does blockchain work",
                    ],
                    title="",
                    description="",
                )

            # === SCRAPE TAB ===
            with gr.Tab("🌐 Scrape"):
                gr.Markdown(
                    "Scrape a web page and analyze its content with AI."
                )

                with gr.Row():
                    with gr.Column():
                        url_input = gr.Textbox(
                            label="URL to Scrape",
                            placeholder="https://example.com",
                            lines=1
                        )
                        question_input = gr.Textbox(
                            label="Question (Optional)",
                            placeholder="What is this page about? Extract key points, etc.",
                            lines=2
                        )
                        scrape_button = gr.Button("Scrape & Analyze", variant="primary")

                    with gr.Column():
                        scrape_output = gr.Textbox(
                            label="Analysis Result",
                            lines=20,
                            max_lines=30
                        )

                # Handle scrape button click
                def handle_scrape(url, question):
                    """Handle scrape button click"""
                    for output in scrape_and_process(url, question, []):
                        yield output

                scrape_button.click(
                    fn=handle_scrape,
                    inputs=[url_input, question_input],
                    outputs=scrape_output
                )

                # Examples
                gr.Examples(
                    examples=[
                        ["https://en.wikipedia.org/wiki/Artificial_intelligence", "What is AI?"],
                        ["https://news.ycombinator.com", "Summarize top stories"],
                    ],
                    inputs=[url_input, question_input],
                )

        # Footer
        gr.Markdown(
            """
            ---
            **Model:** gpt-oss-20b-Q5_K_M | **Framework:** llama-cpp-python | **UI:** Gradio
            """
        )

    return interface


def launch_ui():
    """Launch the Gradio interface"""
    interface = create_interface()

    interface.launch(
        server_name=config.GRADIO_CONFIG["server_name"],
        server_port=config.GRADIO_CONFIG["server_port"],
        share=config.GRADIO_CONFIG["share"],
    )
