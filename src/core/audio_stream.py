"""
音訊流處理模組
負責音訊採集和流管理
"""

import pyaudio
import wave
from collections import deque


class AudioStream:
    """音訊流管理器"""

    def __init__(self, sample_rate=16000, frame_size=480, channels=1):
        """
        初始化音訊流

        Args:
            sample_rate: 取樣率 (Hz)
            frame_size: 幀大小
            channels: 聲道數
        """
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.channels = channels

        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_running = False

        # 音訊緩衝
        self.audio_buffer = deque(maxlen=100)

        # 回呼函式
        self.on_audio_frame = None

    def start(self):
        """啟動音訊流"""
        if self.is_running:
            return

        self.is_running = True

        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.frame_size,
            stream_callback=self._audio_callback
        )

        self.stream.start_stream()
        print("音訊流已啟動")

    def stop(self):
        """停止音訊流"""
        if not self.is_running:
            return

        self.is_running = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        self.audio.terminate()
        print("音訊流已停止")

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """音訊流回呼"""
        if self.is_running:
            self.audio_buffer.append(in_data)

            # 觸發外部回呼
            if self.on_audio_frame:
                self.on_audio_frame(in_data)

        return (in_data, pyaudio.paContinue)

    def save_audio(self, filename, audio_data):
        """
        儲存音訊檔案

        Args:
            filename: 檔案名稱
            audio_data: 音訊資料 (bytes)
        """
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data)

    def list_devices(self):
        """列出可用音訊裝置"""
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxInputChannels']
                })
        return devices
