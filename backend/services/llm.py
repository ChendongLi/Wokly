import logging
import os

logger = logging.getLogger(__name__)

_anthropic_client = None
_openai_client = None


def provider() -> str:
    return os.getenv("AI_PROVIDER", "anthropic").lower()


def _get_anthropic():
    global _anthropic_client
    if _anthropic_client is None:
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        _anthropic_client = anthropic.AsyncAnthropic(api_key=api_key)
    return _anthropic_client


def _get_openai():
    global _openai_client
    if _openai_client is None:
        import openai

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        _openai_client = openai.AsyncOpenAI(api_key=api_key)
    return _openai_client


async def chat(system: str, messages: list[dict], max_tokens: int = 4096) -> tuple[str, str]:
    """Call the configured AI provider. Returns (text, stop_reason).

    stop_reason is normalised: 'end_turn' means complete, 'max_tokens' means truncated.
    """
    p = provider()

    if p == "openai":
        model = os.getenv("OPENAI_MODEL", "gpt-4o")
        openai_messages = [{"role": "system", "content": system}] + messages
        response = await _get_openai().chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=openai_messages,
        )
        choice = response.choices[0]
        text = choice.message.content or ""
        # normalise finish_reason to match Anthropic convention
        stop_reason = "max_tokens" if choice.finish_reason == "length" else "end_turn"
        logger.info(
            "OpenAI response: finish_reason=%s, usage=%s", choice.finish_reason, response.usage
        )
        return text, stop_reason

    else:  # anthropic (default)
        model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
        response = await _get_anthropic().messages.create(
            model=model,
            max_tokens=max_tokens,
            system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            messages=messages,
        )
        block = response.content[0] if response.content else None
        text = block.text if block and block.type == "text" else ""
        logger.info(
            "Anthropic response: stop_reason=%s, usage=%s", response.stop_reason, response.usage
        )
        return text, response.stop_reason
