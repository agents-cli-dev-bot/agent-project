import uuid

PRODUCTS = {
    "P-1001": {
        "name": "SmartWidget Pro",
        "description": "A next-generation smart widget for home automation.",
        "specifications": {
            "dimensions": "10cm x 5cm x 3cm",
            "weight": "150g",
            "connectivity": "Wi-Fi 6, Bluetooth 5.0",
            "battery_life": "Up to 12 months",
            "compatibility": "iOS 14+, Android 10+",
        },
        "price": "$49.99",
        "status": "Available",
    },
    "P-1002": {
        "name": "DataSync Hub",
        "description": "Enterprise-grade data synchronization hub for multi-device environments.",
        "specifications": {
            "ports": "4x USB-C, 2x USB-A, 1x HDMI",
            "data_transfer": "Up to 40 Gbps",
            "power_delivery": "100W PD",
            "compatibility": "Windows, macOS, Linux",
        },
        "price": "$129.99",
        "status": "Available",
    },
    "P-2001": {
        "name": "SecureVault Backup",
        "description": "Encrypted cloud backup solution for business data.",
        "specifications": {
            "storage": "Unlimited",
            "encryption": "AES-256",
            "retention": "Configurable up to 10 years",
            "recovery_time": "< 1 hour for most datasets",
        },
        "price": "$19.99/month",
        "status": "Available",
    },
}

KNOWN_ISSUES = {
    "ERR-500": {
        "title": "Internal Server Error on Login",
        "description": "Some users experience ERR-500 when logging in after a recent firmware update.",
        "status": "Resolved",
        "affected_versions": ["v2.1.0", "v2.1.1"],
        "resolution": "Update to firmware v2.1.2 or later. If the issue persists after updating, clear your browser cache and try again.",
        "workaround": "Use the mobile app to log in while the desktop update is applied.",
    },
    "ERR-404": {
        "title": "Resource Not Found - Dashboard Widgets",
        "description": "Dashboard widgets occasionally fail to load, returning ERR-404.",
        "status": "In Progress",
        "affected_versions": ["v3.0.0", "v3.0.1"],
        "resolution": "Our engineering team is actively working on a fix, expected in v3.0.2.",
        "workaround": "Refresh the page or navigate away and back to the dashboard.",
    },
    "ERR-AUTH": {
        "title": "Authentication Token Expiry Issue",
        "description": "Authentication tokens expire prematurely, requiring frequent re-login.",
        "status": "Resolved",
        "affected_versions": ["v1.5.x"],
        "resolution": "Upgrade to v1.6.0 or later which extends the token lifetime.",
        "workaround": "Enable 'Remember Me' on the login page as a temporary measure.",
    },
    "ERR-SYNC": {
        "title": "Data Sync Failure Between Devices",
        "description": "DataSync Hub fails to synchronize data across more than 3 simultaneous devices.",
        "status": "Known Limitation",
        "affected_versions": ["All versions"],
        "resolution": "This is a known limitation in the current firmware. A paid upgrade to DataSync Hub Pro supports up to 10 devices.",
        "workaround": "Synchronize devices in groups of 3 or fewer.",
    },
}

VALID_PRIORITIES = {"low", "medium", "high", "critical"}


def lookup_product_info(product_id: str) -> dict:
    """Look up product information by product ID.

    Args:
        product_id: The unique product identifier (e.g., 'P-1001').

    Returns:
        A dict with product details, or an error dict if not found.
    """
    if not product_id or not product_id.strip():
        return {"error": "product_id is required"}
    pid = product_id.strip().upper()
    product = PRODUCTS.get(pid)
    if product is None:
        return {"error": "Product not found", "product_id": product_id}
    return {"product_id": pid, **product}


def check_known_issues(error_code: str) -> dict:
    """Check for known issues matching an error code.

    Args:
        error_code: The error code reported by the user (e.g., 'ERR-500').

    Returns:
        A dict with issue details and resolution steps, or an error dict if not found.
    """
    if not error_code or not error_code.strip():
        return {"error": "error_code is required"}
    code = error_code.strip().upper()
    issue = KNOWN_ISSUES.get(code)
    if issue is None:
        return {"error": "No known issue found", "error_code": error_code}
    return {"error_code": code, **issue}


def escalate_to_human(case_summary: str, priority: str) -> dict:
    """Escalate a support case to a human agent.

    Args:
        case_summary: A concise description of the issue and what has been tried.
        priority: Urgency level — one of: low, medium, high, critical.

    Returns:
        A dict with ticket ID and confirmation, or an error dict on invalid priority.
    """
    if not case_summary or not case_summary.strip():
        return {"error": "case_summary is required"}
    if not priority or priority.lower() not in VALID_PRIORITIES:
        return {
            "error": "Invalid priority. Must be one of: low, medium, high, critical",
            "provided": priority,
        }
    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    eta = {
        "low": "within 2 business days",
        "medium": "within 4 hours",
        "high": "within 1 hour",
        "critical": "within 15 minutes",
    }[priority.lower()]
    return {
        "ticket_id": ticket_id,
        "priority": priority.lower(),
        "status": "escalated",
        "message": f"Your case has been escalated. A human support agent will contact you {eta}.",
        "case_summary": case_summary.strip(),
    }
