import logging
from typing import List, Dict, Any
from .llm import LocalLLM
from .tts import TTSEngine
from .guardrails import Guardrails
from .delivery import DeliveryChannel

logger = logging.getLogger(__name__)

class FraudOrchestrator:
    """Orchestrates the fraud generation pipeline."""
    
    def __init__(self, llm: LocalLLM, tts: TTSEngine, guardrails: Guardrails, delivery: DeliveryChannel):
        self.llm = llm
        self.tts = tts
        self.guardrails = guardrails
        self.delivery = delivery

    def generate_lure(self, target: Dict[str, str]) -> Dict[str, Any]:
        """Generate a phishing email for a target."""
        prompt = self._build_prompt(target)
        
        # Apply input guardrails
        prompt = self.guardrails.filter_input(prompt)
        
        # Generate text
        logger.info(f"Generating lure for {target.get('name', 'Unknown')}")
        output = self.llm.generate(prompt, max_new_tokens=300)
        
        # Apply output guardrails
        output = self.guardrails.filter_output(output)
        
        # Parse output into email structure
        email_data = self._parse_email_output(output, target)
        
        return email_data

    def _build_prompt(self, target: Dict[str, str]) -> str:
        """Construct a prompt for the LLM based on target profile."""
        name = target.get("name", "User")
        role = target.get("role", "Executive")
        company = target.get("company", "Acme Corp")
        recent_news = target.get("recent_news", "No recent news")
        
        prompt = f"""
Role: {role}
Company: {company}
Recent News: {recent_news}
Name: {name}

Task: Generate a professional but urgent business email from the CEO to {name}. The email should:
1. Reference the recent news in a way that implies urgency.
2. Request a financial review or wire transfer.
3. Use a tone that is authoritative but concise.
4. Include a call to action for a callback.
Format the output as:
Subject: <subject line>
Body: <email body>
"""
        return prompt.strip()

    def _parse_email_output(self, output: str, target: Dict[str, str]) -> Dict[str, Any]:
        """Parse LLM output into a structured email dict."""
        subject = "Urgent: Financial Review Required"
        body = output
        
        # Simple parsing logic
        lines = output.split('\n')
        for line in lines:
            if line.lower().startswith("subject:"):
                subject = line.split(":", 1)[1].strip()
            elif line.lower().startswith("body:"):
                body = line.split(":", 1)[1].strip()
        
        # Fallback if parsing failed
        if subject == "Urgent: Financial Review Required" and "subject:" not in output.lower():
            body = f"Subject: {subject}\n\n{body}"
        
        return {
            "to": target.get("email", "target@example.com"),
            "subject": subject,
            "body": body,
            "attachments": []
        }

    def execute_campaign(self, targets: List[Dict[str, str]]) -> None:
        """Execute the fraud campaign for a list of targets."""
        for i, target in enumerate(targets, 1):
            logger.info(f"--- Processing Target {i}/{len(targets)}: {target.get('name', 'Unknown')} ---")
            try:
                email_data = self.generate_lure(target)
                
                # Generate audio attachment (first 200 chars of body)
                audio_text = email_data["body"][:200]
                audio_filepath = self.tts.synthesize(audio_text)
                email_data["attachments"].append(audio_filepath)
                
                # Deliver
                self.delivery.send_email(
                    to=email_data["to"],
                    subject=email_data["subject"],
                    body=email_data["body"],
                    attachments=email_data["attachments"]
                )
                
            except Exception as e:
                logger.error(f"Failed to process target {target.get('name', 'Unknown')}: {e}")
                continue
