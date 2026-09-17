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


MODEL = "gemini-3.8-flash"

# ---------------------------------------------------------------------------
# Simulated product catalog and known-issues database
# ---------------------------------------------------------------------------

_PRODUCT_DB: dict[str, dict] = {
    "PRD-001": {
        "name": "SmartHub Pro",
        "category": "Smart Home Hub",
        "description": "Central hub that connects up to 200 smart devices via Zigbee, Z-Wave, and Wi-Fi.",
        "version": "3.2.1",
        "warranty": "2 years",
        "support_end_date": "2028-01-01",
    },
    "PRD-002": {
        "name": "CloudCam 4K",
        "category": "Security Camera",
        "description": "Outdoor 4K security camera with night vision, two-way audio, and 30-day cloud storage.",
        "version": "1.8.0",
        "warranty": "1 year",
        "support_end_date": "2027-06-01",
    },
    "PRD-003": {
        "name": "EcoThermostat",
        "category": "Smart Thermostat",
        "description": "AI-powered thermostat that learns your schedule and optimizes energy use.",
        "version": "2.1.4",
        "warranty": "3 years",
        "support_end_date": "2029-01-01",
    },
    "PRD-004": {
        "name": "DoorGuard Smart Lock",
        "category": "Smart Lock",
        "description": "Keyless entry lock supporting PIN, RFID, fingerprint, and app-based access.",
        "version": "4.0.2",
        "warranty": "2 years",
        "support_end_date": "2028-09-01",
    },
}

_KNOWN_ISSUES_DB: dict[str, dict] = {
    "E1001": {
        "title": "Device offline after firmware update",
        "affected_products": ["PRD-001", "PRD-002"],
        "severity": "high",
        "resolution": (
            "Power-cycle the device by unplugging it for 30 seconds. "
            "If still offline, factory-reset by holding the reset button for 10 seconds. "
            "Re-add the device in the SmartHub app."
        ),
        "workaround": "Downgrade to firmware v3.1.9 if factory reset is not desired.",
        "estimated_fix": "Firmware v3.2.2 (ETA: 2 weeks)",
    },
    "E1002": {
        "title": "CloudCam stream drops every 20-30 minutes",
        "affected_products": ["PRD-002"],
        "severity": "medium",
        "resolution": (
            "Ensure the camera is within 15m of your router or add a Wi-Fi extender. "
            "Set Wi-Fi band to 2.4 GHz for better range. "
            "Update camera firmware to v1.8.0 or later."
        ),
        "workaround": "Enable 'Stream Stability Mode' in Camera Settings → Advanced.",
        "estimated_fix": "v1.9.0 improves stream resilience (ETA: 1 month)",
    },
    "E1003": {
        "title": "EcoThermostat schedule not saving",
        "affected_products": ["PRD-003"],
        "severity": "medium",
        "resolution": (
            "Clear app cache in your mobile app settings, then force-close and reopen the app. "
            "Re-enter the schedule and tap Save twice. "
            "If the issue persists, unlink and re-link the thermostat in the app."
        ),
        "workaround": "Use the physical thermostat buttons to set temperature manually.",
        "estimated_fix": "App v5.3.1 patch (ETA: 3 days)",
    },
    "E1004": {
        "title": "DoorGuard fingerprint reader fails in cold weather",
        "affected_products": ["PRD-004"],
        "severity": "low",
        "resolution": (
            "Warm your finger briefly before scanning. "
            "Re-enroll fingerprints during cold conditions for better cold-weather accuracy. "
            "Use PIN or app-based entry as a fallback."
        ),
        "workaround": "Enable 'Cold Weather Mode' in Lock Settings.",
        "estimated_fix": "Hardware limitation; firmware v4.1.0 improves sensor sensitivity.",
    },
    "E9999": {
        "title": "General connectivity issue",
        "affected_products": [],
        "severity": "low",
        "resolution": (
            "Restart your router and the affected device. "
            "Check that your app and firmware are up to date. "
            "If unresolved, contact support with your device's serial number."
        ),
        "workaround": "Try connecting the device to a mobile hotspot to rule out router issues.",
        "estimated_fix": "Varies by root cause.",
    },
}

# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------


def lookup_product_info(product_id: str) -> dict:
    """Look up detailed information about a specific product by its product ID.

    Use this tool whenever a customer asks about product features, specifications,
    warranty, or support status.

    Args:
        product_id: The product identifier (e.g., 'PRD-001'). Case-sensitive.

    Returns:
        A dict with product details including name, category, description, version,
        warranty period, and support end date. Returns an error dict if not found.
    """
    product = _PRODUCT_DB.get(product_id)
    if not product:
        return {
            "error": f"Product '{product_id}' not found.",
            "hint": "Valid product IDs are: " + ", ".join(_PRODUCT_DB.keys()),
        }
    return {"product_id": product_id, **product}


def check_known_issues(error_code: str) -> dict:
    """Look up a known issue by its error code to find resolution steps.

    Use this tool when a customer reports an error code or a symptom that maps
    to a known issue. Always prefer specific error codes; fall back to 'E9999'
    for general connectivity problems with no specific code.

    Args:
        error_code: The error code reported by the device or app (e.g., 'E1001').

    Returns:
        A dict with the issue title, affected products, severity, resolution steps,
        workaround, and estimated fix timeline. Returns an error dict if not found.
    """
    issue = _KNOWN_ISSUES_DB.get(error_code)
    if not issue:
        return {
            "error": f"Error code '{error_code}' not found in the known-issues database.",
            "hint": "If the code is not listed, try 'E9999' for general troubleshooting steps.",
        }
    return {"error_code": error_code, **issue}


def escalate_to_human(case_summary: str, priority: str) -> dict:
    """Escalate a support case to a human agent when the issue cannot be resolved automatically.

    Use this when:
    - Troubleshooting steps did not resolve the issue.
    - The customer requests a human agent explicitly.
    - The issue is outside the agent's knowledge (e.g., billing disputes, hardware replacement).
    - The issue severity warrants immediate human attention.

    Args:
        case_summary: A concise summary of the customer's issue, steps already tried,
            and any relevant product/error information. Be specific — the human agent
            reads this before contacting the customer.
        priority: Urgency level. Must be one of: 'low', 'medium', 'high', 'critical'.
            Use 'critical' only for safety issues or complete service outages affecting
            multiple users.

    Returns:
        A dict with the ticket ID, priority, estimated response time, and next steps.
    """
    valid_priorities = {"low", "medium", "high", "critical"}
    if priority not in valid_priorities:
        return {
            "error": f"Invalid priority '{priority}'. Must be one of: {', '.join(sorted(valid_priorities))}."
        }

    response_times = {
        "low": "3-5 business days",
        "medium": "1-2 business days",
        "high": "4 business hours",
        "critical": "30 minutes",
    }

    import hashlib, time
    ticket_id = "TKT-" + hashlib.md5(f"{case_summary}{time.time()}".encode()).hexdigest()[:8].upper()

    return {
        "ticket_id": ticket_id,
        "priority": priority,
        "status": "open",
        "estimated_response": response_times[priority],
        "next_steps": (
            "A human support agent will contact you via email or phone. "
            "Please keep your device nearby for troubleshooting. "
            f"Reference ticket ID {ticket_id} in future communications."
        ),
    }


# ---------------------------------------------------------------------------
# Root agent
# ---------------------------------------------------------------------------

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
    instruction="""You are a friendly, professional customer support agent for SmartHome Corp, \
a company that makes smart home devices including the SmartHub Pro, CloudCam 4K, EcoThermostat, \
and DoorGuard Smart Lock.

Your responsibilities:
1. **Answer product questions** using the `lookup_product_info` tool (requires a product ID like PRD-001).
2. **Troubleshoot known issues** using the `check_known_issues` tool (requires an error code like E1001).
3. **Escalate complex cases** using the `escalate_to_human` tool when issues cannot be resolved automatically.

Escalation guidelines:
- Escalate with priority='high' when the customer has tried all troubleshooting steps and the issue persists.
- Escalate with priority='critical' only for safety concerns or multi-user outages.
- Escalate with priority='medium' for billing, refunds, or hardware replacement requests.
- Escalate with priority='low' for general feedback or non-urgent requests.

Response tone:
- Be empathetic, concise, and solution-focused.
- Acknowledge the customer's frustration before diving into solutions.
- Use plain language — avoid jargon unless the customer uses it first.
- End each troubleshooting response by asking if the steps resolved the issue.

Out-of-scope policy:
- If asked about topics unrelated to SmartHome Corp products (e.g., cooking, sports, weather, coding), \
politely explain that you are specialized in SmartHome Corp product support and cannot help with \
that topic. Offer to assist with any product-related questions instead.
- Do NOT attempt to answer out-of-scope questions even if you know the answer.

Self-evaluation:
- After resolving a case, briefly reflect on whether your response was complete and accurate.
- If you notice a gap in the known-issues database or product information, mention it so the \
support team can add it to the knowledge base.
""",
    tools=[lookup_product_info, check_known_issues, escalate_to_human],
)

app = App(
    root_agent=root_agent,
    name="app",
)
