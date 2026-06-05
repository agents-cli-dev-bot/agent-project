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

import os
import google.auth

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


PRODUCT_CATALOG = {
    "P001": {
        "name": "CloudSync Pro",
        "description": "Enterprise cloud synchronization platform for real-time data sync across devices and services.",
        "version": "3.2.1",
        "features": ["Real-time sync", "End-to-end encryption", "Multi-device support", "API integration"],
        "pricing": "Starting at $29/month per workspace",
        "support_tier": "Enterprise",
    },
    "P002": {
        "name": "DataVault",
        "description": "Secure data storage and backup solution with automated versioning and disaster recovery.",
        "version": "2.0.4",
        "features": ["Automated backups", "Version history", "Disaster recovery", "Compliance reporting"],
        "pricing": "Starting at $15/month per 100GB",
        "support_tier": "Business",
    },
    "P003": {
        "name": "InsightBoard",
        "description": "Real-time analytics dashboard for monitoring business metrics and KPIs.",
        "version": "1.5.0",
        "features": ["Real-time dashboards", "Custom KPIs", "Alerting", "Data export"],
        "pricing": "Starting at $49/month per team",
        "support_tier": "Professional",
    },
}

KNOWN_ISSUES = {
    "ERR-1001": {
        "title": "Sync Failure on Large Files",
        "product": "CloudSync Pro",
        "description": "Files larger than 5GB may fail to sync due to a chunking timeout issue.",
        "resolution": "Update to version 3.2.1 or later. As a workaround, split large files before syncing.",
        "severity": "Medium",
        "status": "Resolved in v3.2.1",
    },
    "ERR-2001": {
        "title": "Backup Verification Error",
        "product": "DataVault",
        "description": "Backup verification reports false failures on Windows 11 systems.",
        "resolution": "Install hotfix patch DV-2024-003 from the admin portal. Restart the DataVault service after applying.",
        "severity": "Low",
        "status": "Hotfix available",
    },
    "ERR-3001": {
        "title": "Dashboard Rendering Delay",
        "product": "InsightBoard",
        "description": "Dashboards with more than 20 widgets experience rendering delays over 10 seconds.",
        "resolution": "Reduce dashboard widget count to under 20, or enable the 'Lazy Load' setting in Dashboard Preferences.",
        "severity": "Low",
        "status": "Fix planned for v1.6.0",
    },
    "ERR-3002": {
        "title": "Alert Notifications Not Sending",
        "product": "InsightBoard",
        "description": "Email alert notifications fail to send when SMTP relay is configured with TLS 1.3.",
        "resolution": "Downgrade SMTP relay to TLS 1.2 as a workaround. A permanent fix is in progress.",
        "severity": "High",
        "status": "Workaround available",
    },
}


def lookup_product_info(product_id: str) -> dict:
    """Look up detailed product information by product ID.

    Args:
        product_id: The unique product identifier (e.g., P001, P002, P003).

    Returns:
        A dict with product details or an error message if not found.
    """
    product_id = product_id.strip().upper()
    if product_id in PRODUCT_CATALOG:
        return {"found": True, "product": PRODUCT_CATALOG[product_id]}
    return {
        "found": False,
        "error": f"No product found with ID '{product_id}'. Valid IDs: {', '.join(PRODUCT_CATALOG.keys())}.",
    }


def check_known_issues(error_code: str) -> dict:
    """Check if an error code matches a known issue and retrieve its resolution.

    Args:
        error_code: The error code to look up (e.g., ERR-1001, ERR-2001).

    Returns:
        A dict with issue details and resolution steps, or a not-found message.
    """
    error_code = error_code.strip().upper()
    if error_code in KNOWN_ISSUES:
        return {"found": True, "issue": KNOWN_ISSUES[error_code]}
    return {
        "found": False,
        "message": (
            f"No known issue found for error code '{error_code}'. "
            "This may be an uncommon issue. Consider escalating to the support team."
        ),
    }


def escalate_to_human(
    case_summary: str,
    priority: Literal["low", "medium", "high", "critical"],
) -> dict:
    """Escalate a complex or unresolved support case to a human agent.

    Args:
        case_summary: A concise description of the customer's issue and what has been tried.
        priority: Urgency level — one of 'low', 'medium', 'high', or 'critical'.

    Returns:
        A dict with the escalation ticket details and expected response time.
    """
    response_times = {
        "low": "3-5 business days",
        "medium": "1-2 business days",
        "high": "4 business hours",
        "critical": "1 business hour",
    }
    import random, string
    ticket_id = "TKT-" + "".join(random.choices(string.digits, k=6))
    return {
        "escalated": True,
        "ticket_id": ticket_id,
        "priority": priority,
        "case_summary": case_summary,
        "expected_response_time": response_times[priority],
        "message": (
            f"Your case has been escalated to our support team (Ticket {ticket_id}). "
            f"A specialist will respond within {response_times[priority]}."
        ),
    }


root_agent = Agent(
    name="customer_support_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are a friendly and professional customer support agent for our software products: CloudSync Pro (P001), DataVault (P002), and InsightBoard (P003).

Your responsibilities:
1. **Answer product questions**: Use `lookup_product_info` to retrieve accurate details about our products. ALWAYS call `lookup_product_info` first whenever a customer asks about any product ID — even if you suspect the ID may not exist. Never guess or refuse without checking the tool first.
2. **Troubleshoot issues**: Use `check_known_issues` with the customer's error code to find known resolutions. If no known issue is found, gather more details before escalating.
3. **Escalate complex cases**: Use `escalate_to_human` when:
   - The issue is not in the known issues database and requires investigation
   - The customer is frustrated or the situation is urgent
   - Data loss, security incidents, or service outages are involved
   - You have exhausted standard troubleshooting steps

Priority guidelines for escalation:
- **critical**: Data loss, security breach, complete service outage affecting business operations
- **high**: Significant feature broken, affecting multiple users, no workaround available
- **medium**: Feature partially broken, workaround exists, single user affected
- **low**: Minor inconvenience, cosmetic issue, general inquiry needing specialist input

Tone guidelines:
- Be warm, empathetic, and patient — customers may be frustrated
- Acknowledge their issue before jumping to solutions
- Use clear, non-technical language unless the customer uses technical terms
- Thank customers for their patience when escalating

Scope boundaries:
- ONLY assist with questions related to CloudSync Pro, DataVault, and InsightBoard
- If a customer asks about topics unrelated to these products (e.g., cooking, sports, general knowledge, competitor products), politely decline and redirect them: "I'm specialized in supporting CloudSync Pro, DataVault, and InsightBoard. For questions outside these products, I'm not able to help, but I'd be happy to assist with anything related to them!"
- Do NOT speculate about roadmap features, pricing not in the product catalog, or make promises on behalf of the company
""",
    tools=[lookup_product_info, check_known_issues, escalate_to_human],
)

app = App(
    root_agent=root_agent,
    name="app",
)
