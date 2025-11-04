"""
AI Agent Core Logic
Handles LLM initialization and inference using llama-cpp-python

Token Budget Strategy (n_ctx=2048):
- System prompt: ~50 tokens
- User question: ~50 tokens
- Conversation history: ~200 tokens (last 6 messages)
- AI response: 512 tokens (max_tokens)
- Available for context (search/scrape): ~1,236 tokens
Total: ~2,048 tokens (respects context window limit)
"""

from llama_cpp import Llama
import config
import re
from typing import Iterator, List, Dict


class AIAgent:
    """Main AI Agent class using llama-cpp-python"""

    def __init__(self):
        """Initialize the AI agent with the LLM model"""
        self.llm = None
        self.conversation_history = []
        self.current_mode = "conversation"

    def clean_response(self, text: str) -> str:
        """
        Clean model output by removing reasoning/thinking tokens and patterns

        Args:
            text: Raw model output

        Returns:
            Cleaned response text
        """
        if not text:
            return text

        # Remove special tokens (like <|end|>, <|start|>, <|channel|>, <|message|>)
        text = re.sub(r'<\|[^|]+\|>', '', text)

        # If there are reasoning patterns, try to extract just the final answer
        # Look for common reasoning indicators
        reasoning_patterns = [
            r'^.*?We have a conversation:.*?(?=\n[A-Z]|\n#)',  # Remove "We have a conversation..." blocks
            r'^.*?The answer should.*?(?=\n[A-Z]|\n#)',        # Remove "The answer should..." blocks
            r'^.*?We need to.*?(?=\n[A-Z]|\n#)',               # Remove "We need to..." blocks
            r'^.*?We should.*?(?=\n[A-Z]|\n#)',                # Remove "We should..." blocks
            r'^.*?We\'ll comply\..*?\n',                       # Remove "We'll comply" blocks
            r'^\.\.\.\?\s*\n',                                  # Remove "...?" at start
        ]

        for pattern in reasoning_patterns:
            text = re.sub(pattern, '', text, flags=re.DOTALL | re.MULTILINE)

        # Clean up excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()

        return text

    def load_model(self) -> tuple[bool, str]:
        """
        Load the GGUF model
        Returns: (success: bool, message: str)
        """
        # Check if model exists
        is_valid, message = config.validate_model_path()
        if not is_valid:
            return False, message

        try:
            print(f"Loading model from: {config.MODEL_PATH}")
            print("This may take a minute...")

            self.llm = Llama(
                model_path=str(config.MODEL_PATH),
                n_ctx=config.LLM_CONFIG["n_ctx"],
                n_threads=config.LLM_CONFIG["n_threads"],
                n_batch=config.LLM_CONFIG["n_batch"],
                verbose=config.LLM_CONFIG["verbose"],
            )

            print("Model loaded successfully!")
            return True, "Model loaded successfully"

        except Exception as e:
            error_msg = f"Error loading model: {str(e)}"
            print(error_msg)
            return False, error_msg

    def is_ready(self) -> bool:
        """Check if model is loaded and ready"""
        return self.llm is not None

    def set_mode(self, mode: str):
        """
        Set the current operating mode
        mode: 'conversation', 'search', or 'scrape'
        """
        if mode in config.SYSTEM_PROMPTS:
            self.current_mode = mode
            print(f"Mode set to: {mode}")
        else:
            print(f"Invalid mode: {mode}")

    def get_system_prompt(self) -> str:
        """Get the system prompt for current mode"""
        return config.SYSTEM_PROMPTS.get(self.current_mode, "")

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("Conversation history cleared")

    def chat(self, user_message: str, stream: bool = True) -> Iterator[str] | str:
        """
        Send a message to the LLM and get response

        Args:
            user_message: The user's input message
            stream: Whether to stream the response (True) or return complete response

        Returns:
            Iterator of response chunks if stream=True, complete string if stream=False
        """
        if not self.is_ready():
            yield "Error: Model not loaded. Please load the model first."
            return

        # Build the prompt with system prompt and history
        system_prompt = self.get_system_prompt()

        # Format the prompt (simple conversational format)
        prompt = ""

        # Add conversation history
        for msg in self.conversation_history[-6:]:  # Keep last 6 messages (3 exchanges)
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                prompt += f"User: {content}\n"
            else:
                prompt += f"Assistant: {content}\n"

        # Add current user message
        prompt += f"User: {user_message}\nAssistant:"

        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        try:
            if stream:
                # Stream response - show tokens in real-time
                response_text = ""
                for output in self.llm(
                    prompt,
                    max_tokens=config.LLM_CONFIG["max_tokens"],
                    temperature=config.LLM_CONFIG["temperature"],
                    top_p=config.LLM_CONFIG["top_p"],
                    top_k=config.LLM_CONFIG["top_k"],
                    repeat_penalty=config.LLM_CONFIG["repeat_penalty"],
                    stop=["User:", "\nUser:", "\n\n\n", "<|end|>"],
                    stream=True,
                ):
                    chunk = output["choices"][0]["text"]
                    response_text += chunk
                    # Yield each chunk immediately for real-time streaming
                    yield chunk

                # Clean the complete response before saving to history
                cleaned_response = self.clean_response(response_text)

                # Add cleaned response to history (not the raw one)
                self.conversation_history.append({
                    "role": "assistant",
                    "content": cleaned_response
                })

            else:
                # Get complete response
                output = self.llm(
                    prompt,
                    max_tokens=config.LLM_CONFIG["max_tokens"],
                    temperature=config.LLM_CONFIG["temperature"],
                    top_p=config.LLM_CONFIG["top_p"],
                    top_k=config.LLM_CONFIG["top_k"],
                    repeat_penalty=config.LLM_CONFIG["repeat_penalty"],
                    stop=["User:", "\nUser:", "\n\n\n", "<|end|>"],
                    stream=False,
                )

                response_text = output["choices"][0]["text"]

                # Clean the response
                cleaned_response = self.clean_response(response_text)

                # Add cleaned response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": cleaned_response
                })

                return cleaned_response

        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            print(error_msg)
            if stream:
                yield error_msg
            else:
                return error_msg

    def chat_with_context(self, user_message: str, context: str, stream: bool = True) -> Iterator[str] | str:
        """
        Chat with additional context (for search/scrape modes)

        Args:
            user_message: The user's question/request
            context: Additional context (search results, scraped content, etc.)
            stream: Whether to stream the response

        Returns:
            Iterator of response chunks if stream=True, complete string if stream=False
        """
        # Combine user message with context
        enhanced_message = f"{user_message}\n\n**Context:**\n{context}"

        # Use regular chat method
        return self.chat(enhanced_message, stream=stream)


# Global agent instance (will be initialized in main.py)
agent = None

def get_agent() -> AIAgent:
    """Get the global agent instance"""
    global agent
    if agent is None:
        agent = AIAgent()
    return agent
