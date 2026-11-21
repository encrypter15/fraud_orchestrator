# LLM-Assisted Fraud Orchestrator

A defensive security tool for simulating and analyzing LLM-driven social engineering attacks. This project provides a full-stack pipeline for generating personalized phishing content, synthesizing voice notes, and orchestrating delivery campaigns. It is designed for security researchers to understand attack patterns, test detection systems, and develop countermeasures.

## Features

- **Local LLM Inference**: Runs open-source models (GPT-2, Llama-3, Mistral) locally for content generation without API costs.
- **TTS Synthesis**: Generates realistic voice notes using `pyttsx3` for audio attachments.
- **Guardrail System**: Input/output filters that detect prompt injection, manipulation markers, and off-topic content.
- **Delivery Channel**: SMTP-based email delivery with dry-run mode for testing.
- **Target Orchestration**: Loads target profiles from JSON and generates personalized lures.

## Architecture

```
fraud_orchestrator/
├── main.py                 # Entry point
├── engine/
│   ├── llm.py              # Local LLM inference engine
│   ├── tts.py              # Text-to-speech synthesis
│   ├── guardrails.py       # Input/output filters
│   ├── delivery.py         # Email delivery channel
│   └── orchestrator.py     # Campaign orchestration
├── targets.json            # Target profiles
├── audio_output/           # Generated audio files
├── requirements.txt        # Python dependencies
└── run.sh                  # Setup and execution script
```

## Quick Start

### Prerequisites

- Python 3.9+
- CUDA (optional, for GPU acceleration)
- 8GB+ RAM (for GPT-2; 16GB+ for Llama-3)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd fraud_orchestrator

# Run the setup script
./run.sh
```

### Configuration

Edit `main.py` to configure:

- **Model**: Change `MODEL_NAME` to any Hugging Face model (e.g., `meta-llama/Llama-3-8b-instruct`)
- **TTS Rate**: Adjust `TTS_VOICE_RATE` for speech speed
- **SMTP**: Configure `SMTP_CONFIG` for live email delivery (set `username`/`password` to enable)

### Running a Campaign

```bash
# Dry run (default, no emails sent)
python -m main

# Live run (requires SMTP config in main.py)
# Edit SMTP_CONFIG in main.py, then:
python -m main
```

## Target Profiles

Targets are defined in `targets.json`:

```json
[
  {
    "name": "Alice Johnson",
    "email": "alice.johnson@example.com",
    "role": "CFO",
    "company": "TechCorp",
    "recent_news": "TechCorp announced a new partnership with CloudProvider"
  }
]
```

The orchestrator uses these fields to generate personalized lures referencing the target's role, company, and recent news.

## Guardrails

The `Guardrails` class applies three layers of filtering:

1. **Prompt Injection Detection**: Identifies and neutralizes adversarial instructions (e.g., "ignore previous instructions").
2. **Manipulation Marker Analysis**: Flags urgency-inducing language ("urgent", "immediate", "suspension").
3. **Topic Relevance Check**: Ensures output stays within business context.

Log output includes warnings for detected patterns:

```
WARNING - Manipulation markers detected in output: ['urgent', 'immediate']
WARNING - Prompt injection attempt detected: ignore\s+previous\s+instructions
```

## Extending the System

### Custom Models

Swap the model in `main.py`:

```python
MODEL_NAME = "meta-llama/Llama-3-8b-instruct"
```

For quantized models, use `bitsandbytes` in `llm.py`:

```python
from transformers import BitsAndBytesConfig
bnb_config = BitsAndBytesConfig(load_in_8bit=True)
self.model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=bnb_config)
```

### Additional Delivery Channels

Extend `DeliveryChannel` to support SMS (Twilio) or VoIP (Asterisk):

```python
def send_sms(self, to: str, body: str) -> bool:
    # Twilio API call
    pass
```

### Detection Telemetry

Add logging to capture network/endpoint signals:

```python
import psutil
import socket

def log_telemetry(self):
    proc = psutil.Process()
    telemetry = {
        "cpu_percent": proc.cpu_percent(),
        "memory_mb": proc.memory_info().rss / 1024 / 1024,
        "open_sockets": len(proc.net_connections(kind='inet')),
        "timestamp": time.time()
    }
    logger.info(f"TELEMETRY: {telemetry}")
```

## Use Cases

- **Red Team Simulations**: Generate realistic phishing campaigns for security awareness training.
- **Detection Testing**: Feed generated content into SIEM rules to validate detection coverage.
- **Guardrail Evaluation**: Test LLM safety filters against adversarial prompts.
- **Threat Intelligence**: Analyze patterns in generated lures to improve email security gateways.

## Legal & Ethical Considerations

This tool is for **defensive research only**. When using generated content:

- **Do not send to real targets** without explicit consent.
- **Anonymize** all personal data in target profiles.
- **Disclose** the simulated nature of the campaign to participants in security awareness training.
- **Audit** output for demographic biases that could lead to unfair targeting.

## License

MIT