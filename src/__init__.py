"""
VAD + ASR 自動語音處理系統
"""

from .core.vad import VADProcessor
from .core.asr import ASREngine
from .core.audio_stream import AudioStream
from .services.speech_service import SpeechService

__version__ = "1.0.0"

__all__ = [
    'VADProcessor',
    'ASREngine',
    'AudioStream',
    'SpeechService',
]
