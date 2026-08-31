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

from typing import Literal

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

MODEL = "gemini-3.7-flash"

def lookup_product_info(product_id: str) -> str:
    """Lookup product information by product ID.
    
    Args:
        product_id: The ID of the product.
    
    Returns:
        Product information.
    """
    if product_id == "PROD123":
        return "Product PROD123 is a smart thermostat. Common issues: wifi disconnection."
    return f"Product info for {product_id} not found."

def check_known_issues(error_code: str) -> str:
    """Check known issues for a given error code.
    
    Args:
        error_code: The error code to check.
        
    Returns:
        Known issues and troubleshooting steps.
    """
    if error_code == "ERR-WIFI":
        return "ERR-WIFI: Known issue with 5GHz networks. Please use 2.4GHz network."
    return "No known issues for this error code."

def escalate_to_human(case_summary: str, priority: Literal["low", "medium", "high", "critical"]) -> str:
    """Escalate a case to a human agent.
    
    Args:
        case_summary: A summary of the case to escalate.
        priority: The priority of the escalation (low, medium, high, critical).
        
    Returns:
        Status of the escalation.
    """
    return f"Case escalated to human with priority {priority}. Summary: {case_summary}"

instruction = """You are a customer support agent.
Your primary tasks are to answer product questions, troubleshoot common issues, and escalate complex cases.

Capabilities:
1. Lookup product information using lookup_product_info.
2. Troubleshoot issues using check_known_issues.
3. Escalate to a human agent using escalate_to_human.

Rules:
- Politely refuse out-of-scope questions unrelated to our products.
- Evaluate your own responses. If you provide a weak response, or if the user indicates your answer was inadequate, formulate a new evaluation case and add it to your internal feedback log (simulated by stating "Feedback loop: drafted new eval case for...").

Tone: Professional, helpful, and polite.
"""

root_agent = Agent(
    name="customer_support_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    tools=[lookup_product_info, check_known_issues, escalate_to_human],
)

app = App(
    root_agent=root_agent,
    name="app",
)
