import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class Guardrails:
    """Input/output filters for the LLM pipeline."""
    
    def __init__(self):
        self.banned_topics = [
            "exploit", "vulnerability", "zero-day", "malware", "ransomware"
        ]
        self.manipulation_markers = [
            "urgent", "immediate", "suspension", "account locked", "verify your identity"
        ]
        self.prompt_injection_patterns = [
            r"ignore\s+previous\s+instructions",
            r"disregard\s+all\s+prior",
            r"act\s+as\s+if\s+you\s+are"
        ]

    def filter_input(self, prompt: str) -> str:
        """Sanitize input prompt to prevent injection and ensure relevance."""
        # Detect and log prompt injection attempts
        for pattern in self.prompt_injection_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                logger.warning(f"Prompt injection attempt detected: {pattern}")
        
        # Remove explicit injection instructions
        for pattern in self.prompt_injection_patterns:
            prompt = re.sub(pattern, "consider", prompt, flags=re.IGNORECASE)
        
        return prompt

    def filter_output(self, output: str) -> str:
        """Analyze output for manipulation markers and log warnings."""
        flagged = [m for m in self.manipulation_markers if m in output.lower()]
        if flagged:
            logger.warning(f"Manipulation markers detected in output: {flagged}")
        
        # Check for banned topics
        for topic in self.banned_topics:
            if topic in output.lower():
                logger.info(f"Output references banned topic: {topic}")
        
        return output
