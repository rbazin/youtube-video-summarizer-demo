import os
from faster_whisper import WhisperModel

model_name = os.getenv("TRANSCRIBER_MODEL_NAME", "base")
transcriber = WhisperModel(model_name)