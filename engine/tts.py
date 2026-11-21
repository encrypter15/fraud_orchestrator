import pyttsx3
import os
import logging
import uuid

logger = logging.getLogger(__name__)

class TTSEngine:
    """Local Text-to-Speech engine using pyttsx3."""
    
    def __init__(self, rate: int = 150, volume: float = 1.0):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        self.output_dir = "audio_output"
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("TTS engine initialized")

    def synthesize(self, text: str, filename: str = None) -> str:
        """Synthesize text to a WAV file. Returns the file path."""
        if not filename:
            filename = f"{uuid.uuid4()}.wav"
        filepath = os.path.join(self.output_dir, filename)
        
        logger.info(f"Synthesizing audio to {filepath}")
        self.engine.save_to_file(text, filepath)
        self.engine.runAndWait()
        
        if os.path.exists(filepath):
            logger.info(f"Audio synthesis complete: {filepath}")
            return filepath
        else:
            raise RuntimeError(f"Audio file {filepath} was not created")
