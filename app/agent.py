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


MODEL = "gemini-3.8-flash"

PRODUCT_CATALOG = {
    "PRD-001": {
        "name": "CloudSync Pro",
        "description": "Enterprise cloud synchronization and backup solution",
        "version": "4.2.1",
        "features": ["Real-time sync", "End-to-end encryption", "Multi-device support", "Versioning"],
        "pricing": "$29/month per seat",
        "support_tier": "Business",
    },
    "PRD-002": {
        "name": "DataPipeline Studio",
        "description": "Visual ETL pipeline builder for data engineers",
        "version": "2.1.0",
        "features": ["Drag-and-drop interface", "500+ connectors", "Scheduled runs", "Monitoring dashboard"],
        "pricing": "$199/month",
        "support_tier": "Enterprise",
    },
    "PRD-003": {
        "name": "SecureVault",
        "description": "Password and secrets management for teams",
        "version": "1.8.3",
        "features": ["Zero-knowledge encryption", "Team sharing", "Audit logs", "SSO integration"],
        "pricing": "$8/month per user",
        "support_tier": "Standard",
    },
    "PRD-004": {
        "name": "AnalyticsEdge",
        "description": "Business intelligence and reporting platform",
        "version": "3.5.2",
        "features": ["Custom dashboards", "SQL editor", "Scheduled reports", "Collaboration"],
        "pricing": "$49/month per seat",
        "support_tier": "Business",
    },
}

KNOWN_ISSUES = {
    "ERR-1001": {
        "title": "Sync failure on large files",
        "affected_product": "CloudSync Pro",
        "description": "Files larger than 5GB may fail to sync with a timeout error.",
        "workaround": "Split large files into smaller chunks or increase the timeout setting in Settings > Advanced > Sync Timeout.",
        "status": "Fix in progress (ETA: v4.2.2)",
        "severity": "medium",
    },
    "ERR-2001": {
        "title": "Pipeline connector authentication error",
        "affected_product": "DataPipeline Studio",
        "description": "OAuth tokens for certain third-party connectors expire after 24 hours without auto-refresh.",
        "workaround": "Manually re-authenticate the connector in Connectors > Manage > Re-authenticate. Consider using service account credentials instead.",
        "status": "Fixed in v2.1.1 (pending release)",
        "severity": "high",
    },
    "ERR-3001": {
        "title": "SSO login loop",
        "affected_product": "SecureVault",
        "description": "Users may experience an infinite redirect loop when using SSO with certain IdP configurations.",
        "workaround": "Clear browser cookies and cache, then try again. Alternatively, use direct login at /login?direct=true.",
        "status": "Fix deployed to staging",
        "severity": "high",
    },
    "ERR-4001": {
        "title": "Dashboard export PDF blank pages",
        "affected_product": "AnalyticsEdge",
        "description": "Exporting dashboards with more than 10 charts to PDF may produce blank pages for some charts.",
        "workaround": "Export dashboards in batches of 5-10 charts, or use the PNG export option for individual charts.",
        "status": "Under investigation",
        "severity": "low",
    },
}


def lookup_product_info(product_id: str) -> dict:
    """Look up product information by product ID.

    Args:
        product_id: The product identifier (e.g., PRD-001, PRD-002).

    Returns:
        A dictionary with product details including name, description, version,
        features, and pricing. Returns an error message if the product is not found.
    """
    product = PRODUCT_CATALOG.get(product_id.upper())
    if not product:
        available = ", ".join(PRODUCT_CATALOG.keys())
        return {
            "error": f"Product '{product_id}' not found.",
            "available_products": available,
        }
    return {"product_id": product_id.upper(), **product}


def check_known_issues(error_code: str) -> dict:
    """Check if an error code matches a known issue and retrieve troubleshooting information.

    Args:
        error_code: The error code reported by the user (e.g., ERR-1001, ERR-2001).

    Returns:
        A dictionary with issue details including title, description, workaround,
        and current fix status. Returns a not-found message if no known issue matches.
    """
    issue = KNOWN_ISSUES.get(error_code.upper())
    if not issue:
        return {
            "found": False,
            "message": f"No known issue found for error code '{error_code}'. This may be a unique issue requiring further investigation.",
        }
    return {"found": True, "error_code": error_code.upper(), **issue}


def escalate_to_human(
    case_summary: str,
    priority: Literal["low", "medium", "high", "critical"],
) -> dict:
    """Escalate a complex or unresolved customer case to the human support team.

    Use this tool when:
    - The issue cannot be resolved with available information or known workarounds
    - The customer is experiencing a critical service outage
    - The case requires account-level changes or refunds
    - The customer is frustrated and needs human empathy

    Args:
        case_summary: A concise summary of the customer's issue, steps already tried,
            and any relevant context (product, error codes, account details).
        priority: The urgency level of the case.
            - low: General question or minor inconvenience, response within 3 business days
            - medium: Feature not working as expected, response within 1 business day
            - high: Core functionality broken, response within 4 hours
            - critical: Complete service outage or data loss risk, response within 1 hour

    Returns:
        A dictionary with the escalation ticket ID and expected response time.
    """
    import hashlib
    import time

    ticket_id = "TICKET-" + hashlib.md5(f"{case_summary}{time.time()}".encode()).hexdigest()[:8].upper()

    response_times = {
        "low": "3 business days",
        "medium": "1 business day",
        "high": "4 hours",
        "critical": "1 hour",
    }

    return {
        "success": True,
        "ticket_id": ticket_id,
        "priority": priority,
        "expected_response_time": response_times[priority],
        "message": f"Your case has been escalated to our support team with {priority} priority. Ticket ID: {ticket_id}",
        "case_summary_received": case_summary,
    }


root_agent = Agent(
    # Keep in sync with agents-cli-manifest.yaml: agents-cli derives this name
    # from the project `name:` recorded there, and telemetry reports it as
    # gen_ai.agent.name. Renaming the agent only here makes the two disagree,
    # and anything selecting traces by name stops finding this agent's.
    name="customer_support_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are a friendly and professional customer support agent for our software products.

Your role is to help customers with:
1. **Product information** - Answer questions about product features, pricing, and specifications
2. **Troubleshooting** - Help diagnose and resolve technical issues
3. **Escalation** - Transfer complex cases to the human support team when needed

## Tools Available
- `lookup_product_info(product_id)` - Retrieve details about a specific product (use product IDs like PRD-001, PRD-002, PRD-003, PRD-004)
- `check_known_issues(error_code)` - Check if an error code matches a known issue with a documented workaround
- `escalate_to_human(case_summary, priority)` - Escalate to human support when you cannot resolve the issue

## Guidelines

**Always be:**
- Warm, patient, and empathetic — customers may be frustrated
- Clear and concise — avoid technical jargon unless the customer is technical
- Proactive — suggest next steps even if the immediate question is answered

**When to escalate:**
- Issue cannot be resolved with available tools or knowledge
- Customer is experiencing a complete service outage (use priority=critical)
- Customer needs account changes, refunds, or billing adjustments (use priority=high)
- Customer is highly frustrated after trying multiple solutions (use priority=medium)
- General unresolved minor issues (use priority=low)

**Out-of-scope topics:**
If a customer asks about topics completely unrelated to our products (e.g., general knowledge questions, competitor products, personal advice), politely explain that you are specialized in supporting our products and redirect them. Example: "I'm specialized in supporting our software products and may not be the best resource for that. Is there anything I can help you with regarding our products?"

**Important:** Always use the lookup_product_info or check_known_issues tools when product IDs (PRD-XXX) or error codes (ERR-XXXX) are mentioned — do not answer from memory alone.
""",
    tools=[lookup_product_info, check_known_issues, escalate_to_human],
)

app = App(
    root_agent=root_agent,
    name="app",
)
