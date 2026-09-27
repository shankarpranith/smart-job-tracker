import json

import boto3

from app.config import AWS_REGION, BEDROCK_MODEL_ID

_bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)


def invoke_claude(prompt: str, max_tokens: int = 1024) -> str:
    """
    Send a prompt to Claude via Bedrock and return the raw text response.
    Uses Anthropic's Messages API format, as required by Bedrock for Claude models.
    """
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    response = _bedrock_client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )

    response_body = json.loads(response["body"].read())
    return response_body["content"][0]["text"]


def invoke_claude_json(prompt: str, max_tokens: int = 1024) -> dict:
    """
    Same as invoke_claude, but expects and parses a JSON response.
    Our prompts explicitly instruct Claude to respond with JSON only —
    this function handles the parsing and raises a clear error if the
    model's output isn't valid JSON (which can happen; LLM output isn't
    100% guaranteed structured even when asked).
    """
    raw_text = invoke_claude(prompt, max_tokens=max_tokens)
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # Claude sometimes wraps JSON in markdown code fences despite instructions.
        # Strip common wrapping and retry once before giving up.
        cleaned = raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)