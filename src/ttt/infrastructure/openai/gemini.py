from openai import OpenAI


def gemini(api_key: str, base_url: str) -> OpenAI:
    return OpenAI(
        api_key=api_key,
        base_url=f"{base_url}/v1beta/openai/",
    )
