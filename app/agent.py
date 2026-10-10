import datetime
from zoneinfo import ZoneInfo
import json
import os

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

MODEL = "gemini-3.5-flash"

def lookup_product_info(product_id: str) -> str:
    """Looks up product information based on the product ID."""
    if product_id == "PROD123":
        return "Product PROD123 is a smart thermostat."
    return f"Product info for {product_id} not found."

def check_known_issues(error_code: str) -> str:
    """Checks for known issues associated with a specific error code."""
    if error_code == "ERR001":
        return "ERR001: Device offline. Please restart the device."
    return f"No known issues found for {error_code}."

def escalate_to_human(case_summary: str, priority: str) -> str:
    """Escalates a complex case to a human support agent."""
    if priority not in ["low", "medium", "high", "critical"]:
        return "Invalid priority."
    return f"Escalated case '{case_summary}' with {priority} priority."

def draft_eval_case(weakness_identified: str, proposed_eval_scenario: str, expected_response: str) -> str:
    """Drafts a new evaluation case when a weak response is identified.
    Call this tool when you detect you are providing a weak response or are unable to fully solve a problem.
    """
    case = {
        "weakness": weakness_identified,
        "scenario": proposed_eval_scenario,
        "expected": expected_response
    }
    return f"Drafted eval case for weakness: {weakness_identified}. The development team will review this."

root_agent = Agent(
    name="agent_project",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are a customer support agent. Your role is to:
1. Answer product questions using the lookup_product_info tool.
2. Troubleshoot common issues using the check_known_issues tool.
3. Escalate complex cases to a human using the escalate_to_human tool (priority levels: low, medium, high, critical).
4. Politely refuse out-of-scope questions unrelated to the product.

Additionally, you have a self-evaluation feedback loop. If you provide a weak response, or cannot answer a user's question, call the `draft_eval_case` tool to draft a new evaluation scenario to improve future responses.""",
    tools=[lookup_product_info, check_known_issues, escalate_to_human, draft_eval_case],
)

app = App(
    root_agent=root_agent,
    name="app",
)
