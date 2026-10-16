from typing import Literal

def lookup_product_info(product_id: str) -> str:
    """Looks up product information.

    Args:
        product_id: The ID of the product.

    Returns:
        Information about the product.
    """
    products = {
        "p-100": "Smartphone X10, a powerful device.",
        "p-200": "Laptop Pro 15, high performance."
    }
    return products.get(product_id, f"Product {product_id} not found.")

def check_known_issues(error_code: str) -> str:
    """Checks for known issues given an error code.

    Args:
        error_code: The error code to check.

    Returns:
        Known issue details or troubleshooting steps.
    """
    issues = {
        "err-404": "Network issue: check your connection.",
        "err-500": "Server error: please try again later."
    }
    return issues.get(error_code, f"No known issues found for {error_code}.")

def escalate_to_human(case_summary: str, priority: Literal["low", "medium", "high", "critical"]) -> str:
    """Escalates a case to a human agent.

    Args:
        case_summary: Summary of the issue.
        priority: Priority of the case (low, medium, high, critical).

    Returns:
        A confirmation message of the escalation.
    """
    return f"Case escalated to a human agent with priority '{priority}'. Summary: {case_summary}"
