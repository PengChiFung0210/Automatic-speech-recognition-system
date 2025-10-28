"""
語音服務模組
整合 VAD、ASR 和音訊流，提供統一的語音處理服務
"""

import time
import queue
import threading
import numpy as np
from collections import deque

from ..core.vad import VADProcessor
from ..core.asr import ASREngine
from ..core.audio_stream import AudioStream


class SpeechService:
    """語音處理服務"""

    def __init__(self, config=None):
        """
        初始化語音服務

        Args:
            config: 配置字典
        """
        config = config or {}

        # VAD 配置
        vad_config = config.get('vad', {})
        self.sample_rate = vad_config.get('sample_rate', 16000)
        frame_duration = vad_config.get('frame_duration', 30)

        # ASR 配置
        asr_config = config.get('asr', {})
        self.speech_timeout = asr_config.get('speech_timeout', 1.5)
        self.min_speech_duration = asr_config.get('min_speech_duration', 0.5)

        # 初始化元件
        self.vad = VADProcessor(
            sample_rate=self.sample_rate,
            frame_duration=frame_duration,
            vad_mode=vad_config.get('vad_mode', 3),
            energy_threshold=vad_config.get('energy_threshold', 500)
        )

        self.asr = ASREngine(
            model_size=asr_config.get('model_size', 'base'),
            language=asr_config.get('language', 'zh'),
            device=asr_config.get('device', 'cpu'),
            compute_type=asr_config.get('compute_type', 'int8'),
            model_path=asr_config.get('model_path')
        )

        self.audio_stream = AudioStream(
            sample_rate=self.sample_rate,
            frame_size=self.vad.frame_size
        )

        # 語音狀態
        self.is_speaking = False
        self.speech_frames = []
        self.silence_start = None

        # 識別佇列
        self.recognition_queue = queue.Queue()
        self.recognition_thread = None
        self.is_running = False

        # 回呼函式
        self.on_speech_start = None
        self.on_speech_end = None
        self.on_transcription = None
        self.on_language_change = None

    def start(self):
        """啟動語音服務"""
        if self.is_running:
            return

        self.is_running = True

        # 設定音訊流回呼
        self.audio_stream.on_audio_frame = self._process_audio_frame

        # 啟動音訊流
        self.audio_stream.start()

        # 啟動識別執行緒
        self.recognition_thread = threading.Thread(target=self._recognition_worker)
        self.recognition_thread.daemon = True
        self.recognition_thread.start()

        print("語音服務已啟動")

    def stop(self):
        """停止語音服務"""
        if not self.is_running:
            return

        self.is_running = False

        # 停止音訊流
        self.audio_stream.stop()

        # 等待識別執行緒結束
        if self.recognition_thread:
            self.recognition_thread.join(timeout=2)

        print("語音服務已停止")

    def _process_audio_frame(self, frame):
        """處理音訊幀"""
        is_speech = self.vad.is_speech(frame)

        if is_speech:
            self._handle_speech_frame(frame)
        else:
            self._handle_silence_frame(frame)

    def _handle_speech_frame(self, frame):
        """處理語音幀"""
        if not self.is_speaking:
            # 開始說話
            self.is_speaking = True
            self.speech_frames = []
            print("檢測到語音...")

            if self.on_speech_start:
                self.on_speech_start()

        self.speech_frames.append(frame)
        self.silence_start = None

    def _handle_silence_frame(self, frame):
        """處理靜音幀"""
        if self.is_speaking:
            # 可能是說話中的停頓
            self.speech_frames.append(frame)

            if self.silence_start is None:
                self.silence_start = time.time()
            else:
                # 檢查靜音時長
                silence_duration = time.time() - self.silence_start
                if silence_duration >= self.speech_timeout:
                    self._finalize_speech()

    def _finalize_speech(self):
        """完成語音片段"""
        if not self.speech_frames:
            return

        # 計算語音時長
        duration = len(self.speech_frames) * self.vad.frame_duration / 1000

        if duration >= self.min_speech_duration:
            # 合併音訊幀
            audio_data = b''.join(self.speech_frames)

            # 傳送到識別佇列
            self.recognition_queue.put(audio_data)
            print(f"語音片段已捕獲 ({duration:.2f}秒)，開始識別...")

            if self.on_speech_end:
                self.on_speech_end(duration)

        # 重置狀態
        self.is_speaking = False
        self.speech_frames = []
        self.silence_start = None

    def _recognition_worker(self):
        """識別工作執行緒"""
        while self.is_running:
            try:
                # 從佇列獲取音訊資料
                audio_data = self.recognition_queue.get(timeout=0.1)

                # 轉換為 numpy 陣列
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                # 執行識別
                text = self.asr.transcribe(audio_np)

                if text:
                    print(f"識別結果: {text}")

                    if self.on_transcription:
                        self.on_transcription(text)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"識別錯誤: {e}")

    def set_language(self, language):
        """
        切換識別語言

        Args:
            language: 語言代碼 (zh, yue, en)

        Returns:
            bool: 是否切換成功
        """
        success = self.asr.set_language(language)
        if success and self.on_language_change:
            self.on_language_change(language)
        return success

    def get_current_language(self):
        """獲取當前語言"""
        return self.asr.get_current_language()

    def get_language_name(self):
        """獲取當前語言名稱"""
        return self.asr.get_language_name()

    def get_supported_languages(self):
        """獲取支援的語言列表"""
        return self.asr.SUPPORTED_LANGUAGES
