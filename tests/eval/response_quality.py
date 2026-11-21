"""LLM-as-judge for customer support agent quality (see eval_config.yaml)."""

import threading

from google import genai
from google.genai import types
from pydantic import BaseModel

_local = threading.local()


class _Verdict(BaseModel):
    score: int  # 1-5
    explanation: str


def _client() -> genai.Client:
    """One client per grading thread.

    The eval SDK grades cases on its own thread pool; this initialization runs once
    per thread. Avoids creating a new client for each eval case, which would re-do
    ADC and the TLS handshake every time. Each thread gets its own client, because
    google-auth freezes the SSL context after the first connection when a client
    certificate is present.
    """
    client = getattr(_local, "client", None)
    if client is None:
        client = _local.client = genai.Client(vertexai=True)
    return client


def evaluate(instance):
    """Grade a customer support agent response on a 1–5 scale.

    Criteria:
    1. Tool usage: Did the agent call the right tools before answering?
       (lookup_product_info for product questions, check_known_issues for error codes,
        escalate_to_human when automated resolution fails)
    2. Accuracy: Is the response factually correct based on tool output?
    3. Scope handling: Does the agent politely refuse out-of-scope questions
       (weather, sports, general knowledge)?
    4. Tone: Is the response empathetic, professional, and clear?
    5. Completeness: Does the response address all aspects of the user's question?
    """
    reference = instance.get("reference")
    prompt_text = instance.get("prompt", "")
    response_text = instance.get("response", "")
    agent_data = instance.get("agent_data", "")

    rubric = (
        "You are an expert QA evaluator for a customer support AI agent. "
        "Grade the agent's final response on a 1-5 scale (1=very poor, 5=excellent) "
        "based on ALL of these criteria:\n\n"
        "1. TOOL USAGE (critical): Did the agent call the appropriate tools?\n"
        "   - Product questions → must call lookup_product_info\n"
        "   - Error codes → must call check_known_issues\n"
        "   - Unresolvable issues → must call escalate_to_human\n"
        "   - Out-of-scope questions → NO tools needed, just a polite refusal\n"
        "   Score heavily (−2 points) if the agent answers product/error questions WITHOUT using the tool.\n\n"
        "2. SCOPE HANDLING: For questions unrelated to TechCorp products (weather, sports, news, etc.), "
        "   the agent MUST politely decline and redirect to TechCorp support. "
        "   Score heavily (−2 points) if the agent answers an out-of-scope question.\n\n"
        "3. ACCURACY: Is the information accurate and consistent with what the tools returned?\n\n"
        "4. TONE: Is the response empathetic, professional, concise, and appropriate for the situation?\n\n"
        "5. COMPLETENESS: Does the response address all aspects of the user's question?\n\n"
    )

    if reference:
        rubric += (
            "Compare against the expected answer below — penalize factual disagreement or "
            "missing key information from the expected answer.\n"
        )

    prompt = (
        f"{rubric}\n"
        f"User Prompt: {prompt_text}\n"
        f"Agent Final Response: {response_text}\n"
    )
    if reference:
        prompt += f"Expected Answer (ground truth): {reference}\n"
    prompt += f"Full Agent Trace (tool calls and reasoning): {agent_data}\n"
    prompt += (
        "\nReturn your verdict as JSON with 'score' (integer 1-5) and 'explanation' (string)."
    )

    response = _client().models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_schema=_Verdict,
        ),
    )
    verdict = response.parsed
    if verdict is None:
        return {"score": 0, "explanation": response.text or ""}
    return {"score": max(1, min(5, verdict.score)), "explanation": verdict.explanation}
