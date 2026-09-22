import re
from typing import Literal

IntentType = Literal["grounded_qa", "ship30_essay", "markdown_artifact", "html_artifact"]

class IntentRouter:
    """
    Classifies user intent based on query keywords and instructions.
    """

    @staticmethod
    def classify_intent(query: str) -> IntentType:
        q = query.lower()

        # Check for Ship 30 essay requests
        if any(kw in q for kw in ["ship 30", "ship30", "essay", "long-form article", "write an essay", "atomic essay"]):
            return "ship30_essay"

        # Check for HTML/CSS artifact requests
        if any(kw in q for kw in ["html", "dashboard", "interactive", "ui component", "web page", "css"]):
            return "html_artifact"

        # Check for general framework / markdown artifact requests
        if any(kw in q for kw in ["artifact", "framework", "one-page", "cheatsheet", "playbook", "checklist", "summary table"]):
            return "markdown_artifact"

        # Default to grounded Q&A
        return "grounded_qa"

router = IntentRouter()
