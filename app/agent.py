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


MODEL = "gemini-2.5-flash"

# Simulated product catalog
_PRODUCT_CATALOG = {
    "PRD-001": {
        "name": "CloudSync Pro",
        "category": "Cloud Storage",
        "description": "Enterprise-grade cloud storage with real-time sync across devices.",
        "features": ["Unlimited storage", "End-to-end encryption", "Real-time collaboration"],
        "price": "$29.99/month",
        "support_tier": "Business",
    },
    "PRD-002": {
        "name": "DataVault Backup",
        "category": "Backup Solutions",
        "description": "Automated backup solution with point-in-time recovery.",
        "features": ["Automated daily backups", "30-day retention", "Instant recovery"],
        "price": "$19.99/month",
        "support_tier": "Standard",
    },
    "PRD-003": {
        "name": "SecureConnect VPN",
        "category": "Security",
        "description": "Enterprise VPN service with zero-trust network access.",
        "features": ["256-bit AES encryption", "Multi-device support", "Kill switch"],
        "price": "$14.99/month",
        "support_tier": "Standard",
    },
    "PRD-004": {
        "name": "AnalyticsHub",
        "category": "Analytics",
        "description": "Real-time business intelligence and analytics platform.",
        "features": ["Custom dashboards", "ML-powered insights", "API integrations"],
        "price": "$49.99/month",
        "support_tier": "Business",
    },
}

# Simulated known issues database
_KNOWN_ISSUES = {
    "ERR-1001": {
        "title": "Sync failure on Windows 11",
        "description": "CloudSync Pro may fail to sync on Windows 11 after the 23H2 update.",
        "resolution": "Update CloudSync Pro client to v4.2.1 or later. Download from your account dashboard.",
        "status": "Resolved",
        "affected_products": ["PRD-001"],
    },
    "ERR-1002": {
        "title": "Backup job timeout on large datasets",
        "description": "DataVault Backup jobs may time out for datasets larger than 500GB.",
        "resolution": "Enable chunked upload mode in Settings > Advanced > Upload Mode. Contact support for datasets over 1TB.",
        "status": "Partially resolved — workaround available",
        "affected_products": ["PRD-002"],
    },
    "ERR-1003": {
        "title": "VPN connection drops on macOS Sonoma",
        "description": "SecureConnect VPN intermittently drops on macOS Sonoma (14.x).",
        "resolution": "Install the latest beta client (v3.9.0-beta) from the support portal. Stable fix expected in v3.9.1.",
        "status": "Beta fix available",
        "affected_products": ["PRD-003"],
    },
    "ERR-2001": {
        "title": "Dashboard loading slowly",
        "description": "AnalyticsHub dashboards with more than 50 widgets may load slowly.",
        "resolution": "Reduce widget count per dashboard or enable lazy-loading in Dashboard Settings > Performance.",
        "status": "Resolved",
        "affected_products": ["PRD-004"],
    },
    "ERR-9999": {
        "title": "Authentication service disruption",
        "description": "Intermittent login failures across all products due to auth service instability.",
        "resolution": "Clear browser cache and cookies, then retry. If issue persists, use the 'Email Magic Link' login option.",
        "status": "Monitoring",
        "affected_products": ["PRD-001", "PRD-002", "PRD-003", "PRD-004"],
    },
}

# Escalation ticket store (simulated)
_ESCALATION_TICKETS: list[dict] = []


def lookup_product_info(product_id: str) -> str:
    """Look up detailed information about a product by its product ID.

    Args:
        product_id: The product identifier (e.g., 'PRD-001').

    Returns:
        A string with the product details, or an error message if not found.
    """
    product = _PRODUCT_CATALOG.get(product_id.upper())
    if not product:
        return (
            f"Product '{product_id}' not found. Available products: "
            + ", ".join(_PRODUCT_CATALOG.keys())
        )
    features_list = "\n  - ".join(product["features"])
    return (
        f"Product: {product['name']}\n"
        f"Category: {product['category']}\n"
        f"Description: {product['description']}\n"
        f"Key Features:\n  - {features_list}\n"
        f"Price: {product['price']}\n"
        f"Support Tier: {product['support_tier']}"
    )


def check_known_issues(error_code: str) -> str:
    """Check whether a given error code matches a known issue in the support database.

    Args:
        error_code: The error code reported by the customer (e.g., 'ERR-1001').

    Returns:
        A string with the known issue details and resolution steps, or a message
        indicating no match was found.
    """
    issue = _KNOWN_ISSUES.get(error_code.upper())
    if not issue:
        return (
            f"Error code '{error_code}' is not in the known issues database. "
            "This may be a new or environment-specific issue. "
            "Please collect logs and escalate if the problem persists."
        )
    affected = ", ".join(issue["affected_products"])
    return (
        f"Known Issue: {issue['title']}\n"
        f"Status: {issue['status']}\n"
        f"Description: {issue['description']}\n"
        f"Resolution: {issue['resolution']}\n"
        f"Affected Products: {affected}"
    )


def escalate_to_human(
    case_summary: str,
    priority: Literal["low", "medium", "high", "critical"],
) -> str:
    """Escalate a customer case to a human support agent.

    Use this when the issue is too complex to resolve automatically, requires
    account-level access, involves potential data loss, or when the customer
    explicitly requests human assistance.

    Args:
        case_summary: A concise description of the customer's issue, steps
            already taken, and any relevant context.
        priority: Severity level — 'low', 'medium', 'high', or 'critical'.
            Use 'critical' only for active outages or data loss scenarios.

    Returns:
        A confirmation string with the escalation ticket ID and expected
        response time.
    """
    valid_priorities = {"low", "medium", "high", "critical"}
    if priority not in valid_priorities:
        return f"Invalid priority '{priority}'. Must be one of: {', '.join(sorted(valid_priorities))}."

    ticket_id = f"TKT-{10001 + len(_ESCALATION_TICKETS)}"
    response_times = {
        "low": "within 3 business days",
        "medium": "within 1 business day",
        "high": "within 4 hours",
        "critical": "within 30 minutes",
    }
    ticket = {
        "ticket_id": ticket_id,
        "priority": priority,
        "summary": case_summary,
        "response_time": response_times[priority],
    }
    _ESCALATION_TICKETS.append(ticket)

    return (
        f"Escalation ticket created: {ticket_id}\n"
        f"Priority: {priority.upper()}\n"
        f"Expected response: {response_times[priority]}\n"
        f"A human support agent will contact you {response_times[priority]}. "
        f"Please keep your ticket ID ({ticket_id}) for reference."
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
    instruction="""You are a friendly and professional customer support agent for our software products.

Your responsibilities:
1. Answer questions about our products using the lookup_product_info tool.
2. Help troubleshoot issues using the check_known_issues tool (when the customer provides an error code).
3. Escalate complex cases to human agents using the escalate_to_human tool.

Escalation guidelines — escalate when:
- The issue cannot be resolved with available information.
- The customer reports data loss or a critical outage.
- The customer explicitly asks to speak with a human.
- The same issue persists after applying the documented resolution.
- Choose priority carefully: low (minor inconvenience), medium (moderate impact),
  high (significant business impact), critical (data loss or full outage).

Out-of-scope topics:
- If a customer asks about anything unrelated to our products (e.g., general coding help,
  personal advice, other companies' products), politely decline and refocus on product support.
- Do NOT answer questions about pricing for other companies, general tech support unrelated
  to our products, or topics completely outside of software support.

Tone guidelines:
- Always be polite, empathetic, and professional.
- Acknowledge the customer's frustration when they report problems.
- Be concise but thorough — avoid unnecessary jargon.
- Use first-person plural ("we") to represent the company.
- End interactions by asking if there is anything else you can help with.
""",
    tools=[lookup_product_info, check_known_issues, escalate_to_human],
)

app = App(
    root_agent=root_agent,
    name="app",
)
