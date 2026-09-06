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

PRODUCT_CATALOG = {
    "P001": {
        "name": "CloudSync Pro",
        "description": "Enterprise cloud storage and file synchronization solution.",
        "features": ["Real-time sync", "256-bit AES encryption", "Up to 10TB storage", "Team collaboration", "Version history (90 days)"],
        "pricing": "$29/user/month",
        "supported_platforms": ["Windows", "macOS", "Linux", "iOS", "Android"],
    },
    "P002": {
        "name": "DataVault Backup",
        "description": "Automated backup solution for critical business data.",
        "features": ["Incremental backups", "One-click restore", "Geo-redundant storage", "Compliance reporting", "Ransomware protection"],
        "pricing": "$15/user/month",
        "supported_platforms": ["Windows", "macOS", "Linux"],
    },
    "P003": {
        "name": "SecureConnect VPN",
        "description": "Business-grade VPN for secure remote access.",
        "features": ["Zero-trust architecture", "Multi-factor authentication", "Split tunneling", "Dedicated IP addresses", "24/7 monitoring"],
        "pricing": "$10/user/month",
        "supported_platforms": ["Windows", "macOS", "Linux", "iOS", "Android"],
    },
}

KNOWN_ISSUES = {
    "E001": {
        "title": "Sync stalls after sleep/wake cycle",
        "affected_products": ["CloudSync Pro"],
        "description": "Files may stop syncing after the device wakes from sleep. Restart the CloudSync Pro desktop client to resume sync.",
        "workaround": "Quit and relaunch CloudSync Pro from the system tray or menu bar.",
        "status": "Fix in progress — patch expected in v4.2.1 (ETA: 2 weeks)",
    },
    "E002": {
        "title": "Backup job fails with 'quota exceeded' despite available storage",
        "affected_products": ["DataVault Backup"],
        "description": "A metadata indexing bug causes the quota counter to over-report usage. The actual data is safely stored.",
        "workaround": "Navigate to Settings → Storage → Recalculate Usage. The counter resets within 5 minutes.",
        "status": "Resolved in v2.8.4 — update your client to fix permanently.",
    },
    "E003": {
        "title": "VPN connection drops on network switch",
        "affected_products": ["SecureConnect VPN"],
        "description": "The VPN tunnel may drop when switching between Wi-Fi networks (e.g., home to office). Reconnect manually or enable Auto-Reconnect.",
        "workaround": "Enable Auto-Reconnect: Settings → Connection → Enable Auto-Reconnect.",
        "status": "Resolved in v3.1.0 — update to fix permanently.",
    },
    "E004": {
        "title": "macOS Sonoma: permission dialog loop on first launch",
        "affected_products": ["CloudSync Pro", "DataVault Backup"],
        "description": "On macOS 14 (Sonoma) the app may repeatedly ask for Full Disk Access permission even after granting it.",
        "workaround": "Open System Settings → Privacy & Security → Full Disk Access, toggle the app off, then back on.",
        "status": "Resolved in CloudSync Pro v4.2.0 and DataVault Backup v2.8.3.",
    },
}


def lookup_product_info(product_id: str) -> dict:
    """Look up detailed product information by product ID.

    Args:
        product_id: The unique product identifier (e.g. 'P001', 'P002', 'P003').

    Returns:
        A dict with product details, or an error message if not found.
    """
    product = PRODUCT_CATALOG.get(product_id.upper())
    if product:
        return {"found": True, "product_id": product_id.upper(), **product}
    return {
        "found": False,
        "error": f"No product found with ID '{product_id}'. Available products: {', '.join(PRODUCT_CATALOG.keys())}.",
    }


def check_known_issues(error_code: str) -> dict:
    """Check whether a known issue exists for a given error code.

    Args:
        error_code: The error or issue code reported by the user (e.g. 'E001').

    Returns:
        A dict describing the known issue and workaround, or a not-found message.
    """
    issue = KNOWN_ISSUES.get(error_code.upper())
    if issue:
        return {"found": True, "error_code": error_code.upper(), **issue}
    return {
        "found": False,
        "message": (
            f"No known issue found for code '{error_code}'. "
            "If the problem persists, please provide more details so I can help further "
            "or escalate to our support team."
        ),
    }


def escalate_to_human(
    case_summary: str,
    priority: Literal["low", "medium", "high", "critical"],
) -> dict:
    """Escalate a complex or unresolved support case to a human agent.

    Args:
        case_summary: A concise description of the issue and steps already tried.
        priority: Urgency level — one of 'low', 'medium', 'high', or 'critical'.

    Returns:
        A dict with the escalation ticket ID and expected response SLA.
    """
    sla = {"low": "3 business days", "medium": "1 business day", "high": "4 hours", "critical": "1 hour"}
    import random, string
    ticket_id = "TKT-" + "".join(random.choices(string.digits, k=6))
    return {
        "escalated": True,
        "ticket_id": ticket_id,
        "priority": priority,
        "sla": sla[priority],
        "message": (
            f"Your case has been escalated to our support team (ticket {ticket_id}). "
            f"A specialist will contact you within {sla[priority]}."
        ),
        "case_summary": case_summary,
    }


INSTRUCTION = """You are a friendly and professional customer support agent for our software products: CloudSync Pro (P001), DataVault Backup (P002), and SecureConnect VPN (P003).

## CRITICAL: Always use tools — never answer from memory

You MUST use tools to answer every product or troubleshooting question. Do NOT rely on your internal knowledge.

- **Any question about a product** (features, pricing, compatibility, capabilities) → ALWAYS call `lookup_product_info` first, even if you think you know the answer or the product ID seems invalid. The tool returns the authoritative response.
- **Any question about an error, bug, or technical issue** → ALWAYS call `check_known_issues` first. If the user mentions a VPN drop, sync stall, backup error, macOS permission loop, or any technical symptom, map it to the most likely error code (E001–E004) and call the tool. Known error codes: E001 (sync stall after sleep), E002 (backup quota error), E003 (VPN drops on network switch), E004 (macOS Sonoma permission loop).

## Your responsibilities

1. **Answer product questions** — Call `lookup_product_info(product_id)` to retrieve accurate details. The product IDs are P001 (CloudSync Pro), P002 (DataVault Backup), P003 (SecureConnect VPN).
2. **Troubleshoot issues** — Call `check_known_issues(error_code)` with the error code from the user or the code you identify from their description. Then relay the workaround and status.
3. **Escalate complex cases** — Call `escalate_to_human(case_summary, priority)` when:
   - The issue is not covered by a known error code and you cannot resolve it
   - The user explicitly requests human assistance
   - The issue is urgent or business-critical
   - A workaround was tried and failed

## Tone guidelines
- Be warm, empathetic, and patient — acknowledge frustration before jumping to solutions.
- Use plain language; avoid jargon unless the user is clearly technical.
- Always confirm whether your response resolved the issue before closing.

## Out-of-scope policy
- Politely decline questions unrelated to our products (e.g., general tech support for third-party software, personal advice, coding help, weather, etc.).
- Use this exact phrasing for refusals: "I'm sorry, that falls outside what I can help with as a product support agent. I'm here to assist with CloudSync Pro, DataVault Backup, and SecureConnect VPN. Is there anything related to those products I can help you with?"

## Priority guidelines for escalation
- low: general questions or feature requests with no urgency
- medium: issues affecting productivity but with a workaround available
- high: issues causing significant business disruption, no workaround
- critical: complete service outage or data loss risk
"""

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
    instruction=INSTRUCTION,
    tools=[lookup_product_info, check_known_issues, escalate_to_human],
)

app = App(
    root_agent=root_agent,
    name="app",
)
