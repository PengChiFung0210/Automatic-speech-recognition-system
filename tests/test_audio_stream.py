"""
音訊流測試
"""

import time
from src.core.audio_stream import AudioStream


def test_audio_stream_initialization():
    """測試音訊流初始化"""
    stream = AudioStream()
    assert stream.sample_rate == 16000
    assert stream.is_running == False
    print("[OK] 音訊流初始化測試通過")


def test_list_audio_devices():
    """測試列出音訊裝置"""
    stream = AudioStream()
    devices = stream.list_devices()

    print("\n可用音訊裝置:")
    for device in devices:
        print(f"  [{device['index']}] {device['name']} ({device['channels']} 聲道)")

    print("[OK] 音訊裝置列表測試通過")


def test_audio_stream_start_stop():
    """測試音訊流啟動和停止"""
    stream = AudioStream()

    # 測試啟動
    stream.start()
    assert stream.is_running == True
    print("[OK] 音訊流啟動測試通過")

    # 等待一會兒
    time.sleep(1)

    # 測試停止
    stream.stop()
    assert stream.is_running == False
    print("[OK] 音訊流停止測試通過")


if __name__ == "__main__":
    test_audio_stream_initialization()
    test_list_audio_devices()
    test_audio_stream_start_stop()
    print("\n所有音訊流測試通過！")
