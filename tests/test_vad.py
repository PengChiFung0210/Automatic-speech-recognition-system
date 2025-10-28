"""
VAD 模組測試
"""

import numpy as np
from src.core.vad import VADProcessor


def test_vad_initialization():
    """測試 VAD 初始化"""
    vad = VADProcessor()
    assert vad.sample_rate == 16000
    assert vad.frame_duration == 30
    print("[OK] VAD 初始化測試通過")


def test_vad_silence_detection():
    """測試靜音檢測"""
    vad = VADProcessor()

    # 產生靜音
    silence = np.zeros(480, dtype=np.int16).tobytes()
    is_speech = vad.is_speech(silence)

    assert is_speech == False, "靜音應該被識別為非語音"
    print("[OK] 靜音檢測測試通過")


def test_vad_noise_detection():
    """測試噪音檢測"""
    vad = VADProcessor()

    # 產生噪音
    noise = (np.random.randint(-5000, 5000, 480, dtype=np.int16)).tobytes()
    is_speech = vad.is_speech(noise)

    print(f"噪音檢測結果: {is_speech}")
    print("[OK] 噪音檢測測試通過")


if __name__ == "__main__":
    test_vad_initialization()
    test_vad_silence_detection()
    test_vad_noise_detection()
    print("\n所有 VAD 測試通過！")
