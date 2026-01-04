# app/services/human_patch_interface.py

from typing import Dict, Any, List

def present_suggestions(
    failure_class: str,
    analysis: Dict[str, Any],
    suggestions: List[str],
) -> Dict[str, Any]:
    """
    Returns a structured human-decision payload.
    No patching happens here.
    """

    return {
        "action_required": True,
        "failure_class": failure_class,
        "summary": "Automatic patching stopped due to ambiguity",
        "suggestions": suggestions,
        "instruction": "Choose ONE option and provide implementation details",
    }
