from typing import NewType

from openai import AsyncOpenAI


Gemini = NewType("Gemini", AsyncOpenAI)


def gemini(api_key: str, base_url: str) -> Gemini:
    return Gemini(
        AsyncOpenAI(
            api_key=api_key,
            base_url=f"{base_url}/v1beta/openai/",
        ),
    )
