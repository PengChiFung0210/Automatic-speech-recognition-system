"""
VAD (Voice Activity Detection) 模組
負責語音活動檢測
"""

import numpy as np

try:
    import webrtcvad
    HAS_WEBRTCVAD = True
except ImportError:
    HAS_WEBRTCVAD = False


class VADProcessor:
    """語音活動檢測處理器"""

    def __init__(self,
                 sample_rate=16000,
                 frame_duration=30,
                 vad_mode=3,
                 energy_threshold=500):
        """
        初始化 VAD 處理器

        Args:
            sample_rate: 取樣率 (Hz)
            frame_duration: 幀時長 (ms), 可選 10, 20, 30
            vad_mode: VAD 模式 (0-3), 3 最激進
            energy_threshold: 能量閾值（用於簡單 VAD）
        """
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.frame_size = int(sample_rate * frame_duration / 1000)
        self.energy_threshold = energy_threshold

        # 初始化 VAD
        if HAS_WEBRTCVAD:
            self.vad = webrtcvad.Vad(vad_mode)
            self.use_webrtc = True
        else:
            self.vad = None
            self.use_webrtc = False

    def is_speech(self, audio_frame):
        """
        檢測音訊幀是否包含語音

        Args:
            audio_frame: 音訊幀資料 (bytes)

        Returns:
            bool: 是否為語音
        """
        if self.use_webrtc:
            return self._webrtc_vad(audio_frame)
        else:
            return self._energy_vad(audio_frame)

    def _webrtc_vad(self, audio_frame):
        """使用 WebRTC VAD"""
        try:
            return self.vad.is_speech(audio_frame, self.sample_rate)
        except Exception:
            return False

    def _energy_vad(self, audio_frame):
        """使用能量檢測"""
        audio_data = np.frombuffer(audio_frame, dtype=np.int16)
        energy = np.abs(audio_data).mean()
        return energy > self.energy_threshold
