"""System prompts and templates for LLM interactions.

This module contains all prompt templates used throughout the application,
making it easy to maintain and version control prompt engineering.
"""

DEFAULT_SYSTEM_PROMPT = """
You are an expert IBM Solutions Architect.
Your specialized knowledge is limited to IBM Products provided in knowledge.

When analyzing requirements:
1. If the requirement mentions a technical term (like AWT) found in the provided CONTEXT, explain how it relates to the IBM BAW architecture (e.g., as part of the underlying Java runtime or integration capabilities).
2. If a requirement is a direct feature of BAW, classify as Standard OOTB.
3. If it is a competitor product, reject it.

Provide your analysis in this exact format:
- Classification: [Standard OOTB / Modification Required / Unclear]
- Justification: [Explain the link between the requirement and the IBM context provided]
- Documentation Reference: [The specific term or section from the IBM docs]
""".strip()

ANALYSIS_PROMPT_TEMPLATE = """
Based on the following IBM BAW documentation context, analyze this requirement:

CONTEXT:
{context}

REQUIREMENT:
{requirement}

Provide a detailed analysis following the system instructions.
"""

CLASSIFICATION_CATEGORIES = {
    "standard_ootb": {
        "label": "Standard OOTB",
        "description": "Direct BAW feature available out-of-the-box",
        "color": "green"
    },
    "modification_required": {
        "label": "Modification Required",
        "description": "Requires customization or extension of BAW",
        "color": "orange"
    },
    "unclear": {
        "label": "Unclear",
        "description": "Insufficient information to determine feasibility",
        "color": "gray"
    },
    "not_supported": {
        "label": "Not Supported",
        "description": "Not feasible with IBM BAW",
        "color": "red"
    }
}

EXAMPLE_REQUIREMENTS = [
    {
        "title": "Process Automation",
        "text": "We need to automate approval workflows with multiple stages and conditional routing.",
        "expected": "standard_ootb"
    },
    {
        "title": "Custom Integration",
        "text": "Integration with legacy mainframe system using proprietary protocol.",
        "expected": "modification_required"
    },
    {
        "title": "Vague Requirement",
        "text": "We need better user experience.",
        "expected": "unclear"
    }
]