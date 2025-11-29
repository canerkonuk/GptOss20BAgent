# agent.py
# Stable, CoT-safe ChatML-based agent for GPT-OSS / llama.cpp

from llama_cpp import Llama
import config
import re
from typing import List, Dict


###############################################################################
# ChatML prompt builder (clean + CoT-safe)
###############################################################################

def build_prompt(system_prompt: str, messages: List[Dict[str, str]]) -> str:
    """
    Builds a clean ChatML prompt using:
    <|system|>, <|user|>, <|assistant|>
    """
    out = f"<|system|>\n{system_prompt}\n"

    for msg in messages:
        if msg["role"] == "user":
            out += f"<|user|>\n{msg['content']}\n"
        elif msg["role"] == "assistant":
            out += f"<|assistant|>\n{msg['content']}\n"

    # Model continues as assistant
    out += "<|assistant|>\n"
    return out


###############################################################################
# Output Cleaner (STRONG CoT removal)
###############################################################################

def clean_response(text: str) -> str:
    if not text:
        return ""

    # strip ChatML tags
    text = re.sub(r"<\|[^>]+?>", "", text)

    # Strong anti chain-of-thought filters
    COT_PATTERNS = [
        r"(?i)we need to (answer|explain|think).*",
        r"(?i)let'?s (think|break down|analyze).*",
        r"(?i)step-by-step reasoning.*",
        r"(?i)this means that the correct answer is.*",
        r"(?i)first,.*second,.*third,.*",
        r"(?i)I will now.*",
        r"(?i)as an AI.*I cannot.*",
        r"(?i)the conversation says:.*",
        r"(?i)system prompt.*",
        r"(?i)###.*",
        r"(?i)\bchain[- ]?of[- ]?thought\b.*",
    ]
    for p in COT_PATTERNS:
        text = re.sub(p, "", text)

    # Remove leading garbage newlines/spaces
    return text.strip()


###############################################################################
# Agent Class
###############################################################################

class AIAgent:

    def __init__(self):
        self.llm = None
        self.history: List[Dict] = []
        self.current_mode = "conversation"

    ###########################################################################
    # Model loading
    ###########################################################################
    def load_model(self) -> tuple[bool, str]:
        is_valid, msg = config.validate_model_path()
        if not is_valid:
            return False, msg

        try:
            self.llm = Llama(
                model_path=str(config.MODEL_PATH),
                n_ctx=config.LLM_CONFIG["n_ctx"],
                n_threads=config.LLM_CONFIG["n_threads"],
                n_batch=config.LLM_CONFIG["n_batch"],
                verbose=config.LLM_CONFIG["verbose"],
            )
            return True, "Model loaded successfully"
        except Exception as e:
            return False, f"Error loading model: {e}"

    def is_ready(self):
        return self.llm is not None

    ###########################################################################
    # Mode handling
    ###########################################################################
    def set_mode(self, mode: str):
        if mode in config.SYSTEM_PROMPTS:
            self.current_mode = mode
        else:
            print(f"Invalid mode: {mode}")

    def get_system_prompt(self):
        return (
            config.SYSTEM_PROMPTS[self.current_mode]
            + "\nIMPORTANT: Never reveal chain-of-thought. Provide only short reasoning if needed."
        )

    def clear_history(self):
        self.history = []

    ###########################################################################
    # Chat
    ###########################################################################
    def chat(self, user_message: str, stream: bool = True):

        if not self.is_ready():
            if stream:
                yield "Error: Model not loaded"
                return
            return "Error: Model not loaded"

        # Append user message
        self.history.append({"role": "user", "content": user_message})

        # Limit history size (prevents model drift)
        if len(self.history) > 12:
            self.history = self.history[-12:]

        prompt = build_prompt(self.get_system_prompt(), self.history)

        #######################################################################
        # Streaming mode
        #######################################################################
        if stream:
            buffer = ""

            try:
                for output in self.llm(
                    prompt,
                    max_tokens=config.LLM_CONFIG["max_tokens"],
                    temperature=config.LLM_CONFIG["temperature"],
                    top_p=config.LLM_CONFIG["top_p"],
                    top_k=config.LLM_CONFIG["top_k"],
                    repeat_penalty=config.LLM_CONFIG["repeat_penalty"],
                    stop=["<|user|>", "<|system|>"],
                    stream=True,
                ):
                    chunk = output["choices"][0]["text"]
                    buffer += chunk
                    yield chunk

                cleaned = clean_response(buffer)
                self.history.append({"role": "assistant", "content": cleaned})

            except Exception as e:
                yield f"Error: {e}"

        #######################################################################
        # Non-streaming mode
        #######################################################################
        else:
            try:
                out = self.llm(
                    prompt,
                    max_tokens=config.LLM_CONFIG["max_tokens"],
                    temperature=config.LLM_CONFIG["temperature"],
                    top_p=config.LLM_CONFIG["top_p"],
                    top_k=config.LLM_CONFIG["top_k"],
                    repeat_penalty=config.LLM_CONFIG["repeat_penalty"],
                    stop=["<|user|>", "<|system|>"],
                    stream=False,
                )

                text = out["choices"][0]["text"]
                cleaned = clean_response(text)

                self.history.append({"role": "assistant", "content": cleaned})
                return cleaned

            except Exception as e:
                return f"Error: {e}"

    ###########################################################################
    # Chat with injected context (RAG-style)
    ###########################################################################
    def chat_with_context(self, user_message: str, context: str, stream: bool = True):
        merged = f"{user_message}\n\n[CONTEXT]\n{context}"
        return self.chat(merged, stream=stream)


###############################################################################
# Singleton Factory
###############################################################################

agent = None

def get_agent() -> AIAgent:
    global agent
    if agent is None:
        agent = AIAgent()
    return agent
