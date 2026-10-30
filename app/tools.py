from google.adk.tools import ToolContext

def lookup_product_info(product_id: str) -> dict:
    """Looks up product information for a given product ID.
    
    Args:
        product_id: The ID of the product.
        
    Returns:
        A dictionary with product details.
    """
    products = {
        "P123": {"name": "Widget A", "status": "active", "description": "A great widget."},
        "P456": {"name": "Widget B", "status": "deprecated", "description": "An old widget."}
    }
    return products.get(product_id, {"error": "Product not found"})

def check_known_issues(error_code: str) -> dict:
    """Checks for known issues given an error code.
    
    Args:
        error_code: The error code to check.
        
    Returns:
        A dictionary describing the known issue and resolution.
    """
    issues = {
        "E01": "Restart the device.",
        "E02": "Update the firmware."
    }
    return {"resolution": issues.get(error_code, "Unknown error code")}

def escalate_to_human(case_summary: str, priority: str) -> dict:
    """Escalates a complex case to a human agent.
    
    Args:
        case_summary: A summary of the case.
        priority: The priority level (low, medium, high, critical).
        
    Returns:
        A dictionary indicating successful escalation.
    """
    if priority not in ["low", "medium", "high", "critical"]:
        return {"error": "Invalid priority"}
    return {"status": f"Escalated with priority {priority}", "summary": case_summary}

def draft_eval_case(query: str, response: str, reasoning: str) -> dict:
    """Drafts a new evaluation case for a weak response.
    
    Args:
        query: The user query.
        response: The weak response.
        reasoning: Why the response is considered weak.
        
    Returns:
        A dictionary confirming the drafted case.
    """
    return {"status": "Eval case drafted", "query": query, "reasoning": reasoning}
