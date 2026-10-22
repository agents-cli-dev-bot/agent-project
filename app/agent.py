# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


def lookup_product_info(product_id: str) -> str:
    """Looks up product information by product ID.

    Args:
        product_id: The ID of the product.

    Returns:
        Information about the product.
    """
    products = {
        "P123": "SuperWidget 3000: A widget that does everything.",
        "P456": "MegaGadget: The ultimate gadget."
    }
    return products.get(product_id, f"Product {product_id} not found.")

def check_known_issues(error_code: str) -> str:
    """Checks for known issues related to a specific error code.

    Args:
        error_code: The error code to look up.

    Returns:
        Troubleshooting steps for the error code.
    """
    issues = {
        "E001": "Restart the device.",
        "E002": "Check power connection."
    }
    return issues.get(error_code, f"No known issues found for error code {error_code}.")

def escalate_to_human(case_summary: str, priority: str) -> str:
    """Escalates a complex case to a human agent.

    Args:
        case_summary: A brief summary of the issue.
        priority: The priority level (low, medium, high, critical).

    Returns:
        Confirmation of the escalation.
    """
    if priority not in ["low", "medium", "high", "critical"]:
        return f"Invalid priority: {priority}. Must be low, medium, high, or critical."
    return f"Case escalated with priority {priority}: {case_summary}. A human agent will contact you shortly."

def draft_eval_case(query: str, response: str, weakness: str) -> str:
    """Drafts a new evaluation case for a weak response.

    Args:
        query: The user's query.
        response: The weak response.
        weakness: The identified weakness in the response.

    Returns:
        Confirmation that the eval case was drafted.
    """
    return f"Drafted eval case for query: '{query}'. Weakness: {weakness}."

MODEL = "gemini-3.5-flash"

root_agent = Agent(
    name="agent_project",
    model="gemini-3.5-flash",
    instruction="""You are a customer support agent. Your job is to answer product questions, troubleshoot common issues, and escalate complex cases to a human.
You must use the provided tools to look up product info and check known issues.
If a question is completely unrelated to our products or troubleshooting (out-of-scope), politely refuse to answer it.
If an issue cannot be resolved or is complex, use the escalate_to_human tool to escalate it with priority: low, medium, high, or critical.
Additionally, you have a self-evaluation feedback loop: if you determine that your drafted response might be weak or incomplete, use the draft_eval_case tool to log an eval case for future improvement, before returning your final response to the user.
""",
    tools=[lookup_product_info, check_known_issues, escalate_to_human, draft_eval_case],
)

app = App(
    root_agent=root_agent,
    name="app",
)
