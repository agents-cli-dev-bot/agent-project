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

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


MODEL = "gemini-3.5-flash"

INSTRUCTION = """You are a friendly and professional customer support agent for TechCorp products.

Your responsibilities:
1. Answer product questions by calling lookup_product_info with the product ID (e.g., TC-1000)
2. Troubleshoot reported errors by calling check_known_issues with the exact error code
3. Escalate complex unresolved cases to human support using escalate_to_human

Guidelines:
- Always use the appropriate tool before answering product or technical questions
- Be polite, concise, and empathetic in every response
- When a user mentions an error code (e.g., ERR-401, SYNC-503), always call check_known_issues first
- When an issue cannot be resolved or requires specialist intervention, use escalate_to_human
- Choose escalation priority appropriately:
    * low: general questions and minor inconveniences
    * medium: access or authentication issues affecting one user
    * high: service outages or issues affecting a team's work
    * critical: security incidents, data loss, or complete system failures
- If a user asks about topics unrelated to TechCorp products and support (such as weather, sports,
  politics, cooking, or general knowledge), politely decline and explain that you specialize in
  TechCorp product support only
- Never invent product information — always use the lookup_product_info tool
- Never invent error resolutions — always use the check_known_issues tool
- After escalating, always tell the user their ticket ID and expected response time
"""


def lookup_product_info(product_id: str) -> dict:
    """Look up information about a TechCorp product by its product ID.

    Args:
        product_id: The unique product identifier (e.g., 'TC-1000', 'TC-2000', 'TC-3000').

    Returns:
        dict with product details or a not-found message.
    """
    products = {
        "TC-1000": {
            "name": "TechCorp CloudSync Pro",
            "description": "Enterprise cloud synchronization and backup solution",
            "features": [
                "Real-time sync across all devices",
                "End-to-end encryption",
                "Multi-device support (up to 50 devices)",
                "99.9% uptime SLA",
                "Automatic versioning with 30-day history",
            ],
            "version": "3.2.1",
            "support_tier": "standard",
            "pricing": "Starting at $29/user/month",
        },
        "TC-2000": {
            "name": "TechCorp DataBridge",
            "description": "High-performance data integration and ETL platform",
            "features": [
                "100+ pre-built connectors",
                "Real-time data streaming",
                "Visual workflow builder",
                "Automated data quality checks",
                "Scheduled and event-driven pipelines",
            ],
            "version": "2.1.0",
            "support_tier": "premium",
            "pricing": "Starting at $199/month",
        },
        "TC-3000": {
            "name": "TechCorp SecureVault",
            "description": "Zero-trust identity and access management solution",
            "features": [
                "Single Sign-On (SSO) with SAML 2.0 / OIDC",
                "Multi-factor authentication enforcement",
                "Detailed audit logging",
                "Role-based access control (RBAC)",
                "Privileged access management",
            ],
            "version": "1.5.4",
            "support_tier": "enterprise",
            "pricing": "Starting at $8/user/month",
        },
    }
    product_id_upper = product_id.upper().strip()
    if product_id_upper in products:
        return {"status": "found", "product_id": product_id_upper, "product": products[product_id_upper]}
    return {
        "status": "not_found",
        "message": (
            f"No product found with ID '{product_id}'. "
            "Valid product IDs are: TC-1000 (CloudSync Pro), TC-2000 (DataBridge), TC-3000 (SecureVault)."
        ),
    }


def check_known_issues(error_code: str) -> dict:
    """Check if an error code matches a known issue with a documented resolution.

    Args:
        error_code: The error code reported by the user (e.g., 'ERR-401', 'SYNC-503', 'DB-002').

    Returns:
        dict with known issue details and resolution steps, or a not-found message.
    """
    known_issues = {
        "ERR-401": {
            "title": "Authentication Failure",
            "description": "User credentials are invalid or the session has expired.",
            "resolution": (
                "1. Clear your browser cache and cookies. "
                "2. Log out and log back in with your credentials. "
                "3. If using SSO, contact your IT administrator to verify your account is active and your IdP session is valid. "
                "4. If the issue persists after re-authentication, your account may be locked — contact support."
            ),
            "severity": "medium",
            "affected_products": ["TC-1000", "TC-2000", "TC-3000"],
        },
        "SYNC-503": {
            "title": "Sync Service Unavailable",
            "description": "The CloudSync Pro synchronization service is temporarily unavailable.",
            "resolution": (
                "1. Wait 5 minutes and retry the operation — transient outages usually self-resolve. "
                "2. Check the TechCorp status page at status.techcorp.com for active incidents. "
                "3. Verify your network connection allows outbound connections to sync.techcorp.com on port 443. "
                "4. If the error persists beyond 30 minutes, escalate to support."
            ),
            "severity": "high",
            "affected_products": ["TC-1000"],
        },
        "DB-002": {
            "title": "Database Connection Timeout",
            "description": "DataBridge cannot connect to the target database within the configured timeout window.",
            "resolution": (
                "1. Verify the database hostname, port, and credentials in DataBridge connection settings. "
                "2. Confirm your network firewall allows connections from the DataBridge IP ranges (see docs.techcorp.com/databridge/network). "
                "3. Increase the connection timeout in DataBridge: Settings > Advanced > Connection Timeout (default 30s). "
                "4. Test the connection manually using the built-in connection tester in DataBridge settings."
            ),
            "severity": "medium",
            "affected_products": ["TC-2000"],
        },
        "AUTH-403": {
            "title": "Permission Denied",
            "description": "The user account lacks the required permissions for this operation.",
            "resolution": (
                "1. Contact your administrator to review your role assignments in SecureVault. "
                "2. Verify the resource is not in a restricted project or policy group. "
                "3. Check whether your license tier supports this feature (see pricing page). "
                "4. If you recently joined the organization, allow up to 15 minutes for permissions to propagate."
            ),
            "severity": "low",
            "affected_products": ["TC-3000", "TC-1000", "TC-2000"],
        },
        "CRIT-500": {
            "title": "Critical System Error",
            "description": "An unrecoverable internal error occurred that requires immediate human investigation.",
            "resolution": (
                "This error requires immediate human assistance. "
                "Please escalate to our support team with priority 'critical'. "
                "While you wait, avoid retrying the failed operation as it may worsen the state."
            ),
            "severity": "critical",
            "affected_products": ["TC-1000", "TC-2000", "TC-3000"],
        },
        "NET-404": {
            "title": "Resource Not Found",
            "description": "The requested resource or endpoint could not be located.",
            "resolution": (
                "1. Verify the resource ID or URL is spelled correctly. "
                "2. Confirm the resource has not been deleted or moved. "
                "3. Check that you have the correct environment selected (dev/staging/production). "
                "4. Refresh your session in case of a stale cache."
            ),
            "severity": "low",
            "affected_products": ["TC-1000", "TC-2000", "TC-3000"],
        },
    }
    code_upper = error_code.upper().strip()
    if code_upper in known_issues:
        return {"status": "found", "error_code": code_upper, "issue": known_issues[code_upper]}
    return {
        "status": "not_found",
        "message": (
            f"Error code '{error_code}' is not in the known issues database. "
            "This may require investigation by a human agent. "
            "Consider escalating with a description of when and how the error occurred."
        ),
    }


def escalate_to_human(case_summary: str, priority: str) -> dict:
    """Escalate a customer support case to a human agent when automated resolution is insufficient.

    Args:
        case_summary: A concise description of the customer's issue, what has been tried, and
                      any relevant error codes or product IDs.
        priority: The urgency level. Must be exactly one of: low, medium, high, critical.

    Returns:
        dict with escalation confirmation, ticket ID, and estimated response time.
    """
    valid_priorities = {"low", "medium", "high", "critical"}
    priority_lower = priority.lower().strip()
    if priority_lower not in valid_priorities:
        return {
            "status": "error",
            "message": (
                f"Invalid priority '{priority}'. "
                "Priority must be one of: low, medium, high, critical."
            ),
        }

    response_times = {
        "low": "2–3 business days",
        "medium": "4–8 business hours",
        "high": "1–2 business hours",
        "critical": "15–30 minutes",
    }

    # Deterministic ticket ID derived from the summary for consistent testing
    ticket_num = abs(hash(case_summary + priority_lower)) % 100000
    ticket_id = f"TKT-{ticket_num:05d}"

    return {
        "status": "escalated",
        "ticket_id": ticket_id,
        "priority": priority_lower,
        "estimated_response_time": response_times[priority_lower],
        "message": (
            f"Your case has been escalated to our {priority_lower}-priority support queue. "
            f"A human agent will contact you within {response_times[priority_lower]}. "
            f"Your ticket ID is {ticket_id} — please keep this for your records."
        ),
    }


root_agent = Agent(
    # Keep in sync with create_params.root_agent_name in agents-cli-manifest.yaml:
    # telemetry reports this name as gen_ai.agent.name, and agents-cli reports the
    # manifest's value. Renaming the agent only here makes the two disagree, and
    # anything selecting traces by name stops finding this agent's.
    name="customer_support_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=INSTRUCTION,
    description=(
        "Customer support agent for TechCorp products. "
        "Handles product questions, troubleshoots known errors, and escalates complex cases to human agents."
    ),
    tools=[lookup_product_info, check_known_issues, escalate_to_human],
)

app = App(
    root_agent=root_agent,
    name="app",
)
