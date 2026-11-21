import json
import logging
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from .engine.llm import LocalLLM
from .engine.tts import TTSEngine
from .engine.guardrails import Guardrails
from .engine.delivery import DeliveryChannel
from .engine.orchestrator import FraudOrchestrator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_targets_from_file(filepath: str) -> List[Dict[str, str]]:
    """Load target profiles from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            targets = json.load(f)
        if not isinstance(targets, list):
            raise ValueError("Target file must contain a JSON array")
        return targets
    except Exception as e:
        logger.error(f"Failed to load targets from {filepath}: {e}")
        raise

def main():
    # Configuration
    MODEL_NAME = "gpt2"  # Use a small model for demonstration; can be swapped for Llama-3
    TTS_VOICE_RATE = 150  # Words per minute
    SMTP_CONFIG = {
        "host": "localhost",
        "port": 587,
        "username": None,
        "password": None,
        "use_tls": True
    }
    TARGETS_FILE = "targets.json"

    # Initialize Components
    logger.info(f"Initializing LLM: {MODEL_NAME}")
    llm = LocalLLM(model_name=MODEL_NAME)
    tts = TTSEngine(rate=TTS_VOICE_RATE)
    guardrails = Guardrails()
    delivery = DeliveryChannel(smtp_config=SMTP_CONFIG)
    orchestrator = FraudOrchestrator(llm=llm, tts=tts, guardrails=guardrails, delivery=delivery)

    # Load Targets
    logger.info(f"Loading targets from {TARGETS_FILE}")
    targets = load_targets_from_file(TARGETS_FILE)
    logger.info(f"Loaded {len(targets)} targets")

    # Execute Campaign
    orchestrator.execute_campaign(targets)
    logger.info("Campaign execution complete.")

if __name__ == "__main__":
    main()
