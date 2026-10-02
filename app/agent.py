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

import hashlib
import time

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


MODEL = "gemini-2.5-flash"

PRODUCT_CATALOG = {
    "PRD-001": {
        "name": "CloudSync Pro",
        "description": "Enterprise cloud synchronization platform",
        "version": "4.2.1",
        "price": "$49/month",
        "features": ["Real-time sync", "256-bit encryption", "99.9% uptime SLA"],
    },
    "PRD-002": {
        "name": "DataVault",
        "description": "Secure data storage and backup solution",
        "version": "2.1.0",
        "price": "$29/month",
        "features": ["Automated backups", "Point-in-time recovery", "Cross-region replication"],
    },
    "PRD-003": {
        "name": "StreamLine API",
        "description": "High-performance REST API gateway",
        "version": "1.5.3",
        "price": "$99/month",
        "features": ["Rate limiting", "OAuth 2.0", "Analytics dashboard"],
    },
}

KNOWN_ISSUES = {
    "ERR-404": {
        "title": "Resource Not Found",
        "description": "The requested resource could not be located.",
        "resolution": "Verify the resource ID and ensure it exists in your account.",
        "status": "documented",
    },
    "ERR-503": {
        "title": "Service Temporarily Unavailable",
        "description": "The service is experiencing high load or maintenance.",
        "resolution": "Wait 5-10 minutes and retry. Check the status page at status.example.com.",
        "status": "documented",
    },
    "ERR-AUTH-001": {
        "title": "Authentication Token Expired",
        "description": "Your authentication token has expired.",
        "resolution": "Re-authenticate using your credentials to obtain a new token.",
        "status": "documented",
    },
    "ERR-SYNC-002": {
        "title": "Sync Conflict Detected",
        "description": "Conflicting changes detected during synchronization.",
        "resolution": "Open the conflict resolver in the dashboard and manually merge the changes.",
        "status": "documented",
    },
}


def lookup_product_info(product_id: str) -> str:
    """Look up product information by product ID.

    Args:
        product_id: The unique product identifier (e.g., 'PRD-001').

    Returns:
        A string with product details including name, description, features, and pricing.
    """
    product = PRODUCT_CATALOG.get(product_id.upper())
    if not product:
        available = ", ".join(PRODUCT_CATALOG.keys())
        return f"No product found with ID '{product_id}'. Available product IDs: {available}."
    features = ", ".join(product["features"])
    return (
        f"Product: {product['name']} ({product_id.upper()})\n"
        f"Description: {product['description']}\n"
        f"Version: {product['version']}\n"
        f"Price: {product['price']}\n"
        f"Features: {features}"
    )


def check_known_issues(error_code: str) -> str:
    """Check if an error code matches a known issue and return resolution steps.

    Args:
        error_code: The error code to look up (e.g., 'ERR-404', 'ERR-503').

    Returns:
        A string with the issue description and recommended resolution steps,
        or a message indicating the error code is not in the known issues database.
    """
    issue = KNOWN_ISSUES.get(error_code.upper())
    if not issue:
        known = ", ".join(KNOWN_ISSUES.keys())
        return (
            f"Error code '{error_code}' is not in our known issues database. "
            f"Known codes: {known}. "
            "Please provide additional context so I can assist further."
        )
    return (
        f"Known Issue: {issue['title']} ({error_code.upper()})\n"
        f"Description: {issue['description']}\n"
        f"Resolution: {issue['resolution']}\n"
        f"Status: {issue['status']}"
    )


def escalate_to_human(case_summary: str, priority: str) -> str:
    """Escalate a complex case to a human support agent.

    Args:
        case_summary: A brief summary of the customer's issue and context.
        priority: Priority level for the escalation. Must be one of:
                  'low', 'medium', 'high', or 'critical'.

    Returns:
        A confirmation message with an escalation ticket ID and expected response time.
    """
    valid_priorities = {"low", "medium", "high", "critical"}
    priority_lower = priority.lower()
    if priority_lower not in valid_priorities:
        return (
            f"Invalid priority '{priority}'. "
            f"Must be one of: {', '.join(sorted(valid_priorities))}."
        )

    response_times = {
        "low": "24-48 hours",
        "medium": "4-8 hours",
        "high": "1-2 hours",
        "critical": "15-30 minutes",
    }

    ticket_id = "ESC-" + hashlib.md5(
        f"{case_summary}{time.time()}".encode()
    ).hexdigest()[:8].upper()

    return (
        f"Escalation created successfully.\n"
        f"Ticket ID: {ticket_id}\n"
        f"Priority: {priority_lower.upper()}\n"
        f"Summary: {case_summary}\n"
        f"Expected response time: {response_times[priority_lower]}\n"
        "A human support agent will contact you shortly."
    )


root_agent = Agent(
    # Keep in sync with agents-cli-manifest.yaml: agents-cli derives this name
    # from the project `name:` recorded there, and telemetry reports it as
    # gen_ai.agent.name. Renaming the agent only here makes the two disagree,
    # and anything selecting traces by name stops finding this agent's.
    name="agent_project",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are a professional customer support agent for our software products. \
Your role is to assist customers with questions and issues related to our three products: \
CloudSync Pro (PRD-001), DataVault (PRD-002), and StreamLine API (PRD-003).

## What you can help with

1. **Product information**: Use the lookup_product_info tool to provide accurate details \
about our products including features, pricing, and versions.

2. **Troubleshooting**: Use the check_known_issues tool when a customer reports an error code. \
Provide clear, step-by-step resolution guidance based on the tool output.

3. **Escalation**: When an issue cannot be resolved through standard troubleshooting, or when \
the customer's situation is urgent, use the escalate_to_human tool. Choose priority carefully:
   - low: General questions, minor inconveniences, non-urgent feature requests
   - medium: Functionality issues affecting the customer's workflow
   - high: Significant service disruption impacting business operations
   - critical: Complete service outage, data loss risk, or security incident

## What is out of scope

If a customer asks about topics unrelated to our products — such as general knowledge questions, \
competitor products, personal advice, or anything not related to CloudSync Pro, DataVault, or \
StreamLine API — respond politely with:

"I'm sorry, but that question falls outside the scope of our product support. I'm here to help \
with questions about our software products (CloudSync Pro, DataVault, StreamLine API), \
troubleshooting known issues, and escalating complex cases to our team. Is there anything \
related to our products I can help you with today?"

## Tone guidelines

- Be professional, empathetic, and patient at all times
- Acknowledge the customer's frustration when they express it
- Be concise and clear — avoid jargon
- Always confirm what you've done and what the customer should expect next
- End interactions with an offer to help with anything else""",
    tools=[lookup_product_info, check_known_issues, escalate_to_human],
)

app = App(
    root_agent=root_agent,
    name="app",
)
