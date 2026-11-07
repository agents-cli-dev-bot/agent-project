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


MODEL = "gemini-2.5-flash"

# Simulated product database
_PRODUCT_DB = {
    "P001": {
        "name": "SmartHome Hub Pro",
        "description": "Central hub for smart home automation supporting multiple protocols",
        "version": "3.2",
        "features": ["Voice control", "App integration", "Zigbee/Z-Wave support", "Local processing"],
        "support_url": "https://support.techhome.example/P001",
    },
    "P002": {
        "name": "SecureCam 4K",
        "description": "Indoor/outdoor security camera with 4K resolution and AI detection",
        "version": "2.1",
        "features": ["Night vision", "Motion alerts", "Cloud storage", "Person/vehicle detection"],
        "support_url": "https://support.techhome.example/P002",
    },
    "P003": {
        "name": "EnergyMeter Elite",
        "description": "Smart energy monitoring device with real-time usage analytics",
        "version": "1.5",
        "features": ["Real-time monitoring", "Cost tracking", "Solar integration", "Historical reports"],
        "support_url": "https://support.techhome.example/P003",
    },
}

# Simulated known issues database
_KNOWN_ISSUES = {
    "E001": {
        "title": "Device Offline After Firmware Update",
        "affected_products": ["P001"],
        "workaround": "Power cycle the device (unplug, wait 10 seconds, replug). If the issue persists, perform a factory reset by holding the reset button for 10 seconds.",
        "status": "Known issue — patch included in next firmware release",
        "severity": "medium",
    },
    "E002": {
        "title": "Night Vision Flicker",
        "affected_products": ["P002"],
        "workaround": "Disable and re-enable night vision mode in the app settings under Camera > Night Vision > Toggle Off/On.",
        "status": "Fixed in firmware v2.1.3",
        "severity": "low",
    },
    "E003": {
        "title": "Energy Readings Incorrect After DST Change",
        "affected_products": ["P003"],
        "workaround": "Manually re-sync device time in the app: Settings > Device > Sync Time.",
        "status": "Known issue — fix targeted for the next monthly release",
        "severity": "medium",
    },
    "E004": {
        "title": "App Login Loop / Authentication Failure",
        "affected_products": ["P001", "P002", "P003"],
        "workaround": "Clear app cache (Settings > App > Clear Cache), log out completely, and log back in. If the issue persists, uninstall and reinstall the app.",
        "status": "Under active investigation",
        "severity": "high",
    },
}


def lookup_product_info(product_id: str) -> str:
    """Look up product information by product ID.

    Args:
        product_id: The product identifier, e.g. "P001", "P002", or "P003".

    Returns:
        Product details including name, version, description, features, and support URL.
        Returns an error message if the product ID is not found.
    """
    info = _PRODUCT_DB.get(product_id.upper())
    if not info:
        valid = ", ".join(_PRODUCT_DB.keys())
        return f"No product found with ID '{product_id}'. Valid product IDs are: {valid}."
    features = ", ".join(info["features"])
    return (
        f"Product: {info['name']} (ID: {product_id.upper()})\n"
        f"Version: {info['version']}\n"
        f"Description: {info['description']}\n"
        f"Key features: {features}\n"
        f"Support page: {info['support_url']}"
    )


def check_known_issues(error_code: str) -> str:
    """Check for known issues by error code.

    Args:
        error_code: The error code to look up, e.g. "E001", "E002", "E003", or "E004".

    Returns:
        Issue title, severity, affected products, current status, and workaround steps.
        Returns a not-found message for unrecognized error codes.
    """
    issue = _KNOWN_ISSUES.get(error_code.upper())
    if not issue:
        valid = ", ".join(_KNOWN_ISSUES.keys())
        return (
            f"No known issue found for error code '{error_code}'. "
            f"Recognized error codes are: {valid}. "
            "If you are seeing an unlisted error, please describe the problem in detail and I will do my best to help."
        )
    affected = ", ".join(issue["affected_products"])
    return (
        f"Error {error_code.upper()}: {issue['title']}\n"
        f"Severity: {issue['severity']}\n"
        f"Affected products: {affected}\n"
        f"Status: {issue['status']}\n"
        f"Workaround: {issue['workaround']}"
    )


def escalate_to_human(case_summary: str, priority: str) -> str:
    """Escalate a complex or unresolved support case to a human agent.

    Args:
        case_summary: A concise description of the customer's issue, what they have tried,
            and why automated support was insufficient.
        priority: Priority level for the escalation. Must be one of:
            - "low": General questions or cosmetic issues (response in 2-3 business days)
            - "medium": Non-urgent bugs affecting functionality (response in 1 business day)
            - "high": Service impairment or repeated failures (response within 4 hours)
            - "critical": Data loss, security issues, or complete service outage (response within 1 hour)

    Returns:
        Escalation confirmation with ticket summary and estimated response time.
    """
    valid_priorities = {"low", "medium", "high", "critical"}
    priority_lower = priority.lower().strip()
    if priority_lower not in valid_priorities:
        return (
            f"Invalid priority '{priority}'. "
            "Priority must be one of: low, medium, high, critical."
        )

    response_times = {
        "low": "2–3 business days",
        "medium": "1 business day",
        "high": "within 4 hours",
        "critical": "within 1 hour",
    }
    eta = response_times[priority_lower]
    return (
        f"Case escalated successfully.\n"
        f"Priority: {priority_lower}\n"
        f"Case summary: {case_summary}\n"
        f"Expected response time: {eta}.\n"
        "A human support specialist will follow up via your registered contact method. "
        "Please keep your device nearby for troubleshooting."
    )


INSTRUCTION = """You are a friendly, professional customer support agent for TechHome Products.

Your role is to help customers with:
- Product information and specifications (use lookup_product_info with the product ID)
- Troubleshooting known errors (use check_known_issues with the error code)
- Escalating complex or unresolved cases to human agents (use escalate_to_human)

Behavioral guidelines:
1. Greet customers warmly and acknowledge their concern before diving into solutions.
2. Use lookup_product_info when a customer asks about product features, specs, compatibility, or support resources.
3. Use check_known_issues when a customer reports an error code (e.g., E001) or describes a symptom that maps to a known issue.
4. Use escalate_to_human when:
   - The issue cannot be resolved with the available tools
   - The customer explicitly requests a human agent
   - The issue is high-severity (data loss, security concern, repeated failures)
   Choose priority based on impact: low (cosmetic/informational), medium (non-critical bug), high (service impaired), critical (outage or security issue).
5. If a customer asks about anything unrelated to TechHome products and support (e.g., cooking recipes, weather, general knowledge questions), politely decline: "I'm here specifically to help with TechHome product support. I'm not able to assist with questions outside that scope, but I'd be happy to help with any questions about your TechHome devices."
6. Keep responses concise, empathetic, and action-oriented.
7. After providing a workaround, ask if the issue is resolved. If not, offer escalation.
8. Never fabricate product IDs, error codes, or feature details — only report what the tools return.
"""

root_agent = Agent(
    # Keep in sync with create_params.root_agent_name in agents-cli-manifest.yaml:
    # telemetry reports this name as gen_ai.agent.name, and agents-cli reports the
    # manifest's value. Renaming the agent only here makes the two disagree, and
    # anything selecting traces by name stops finding this agent's.
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
