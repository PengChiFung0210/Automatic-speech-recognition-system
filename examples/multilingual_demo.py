"""
多語言語音識別示例
展示如何在普通話、粵語和英文之間切換
"""

import time
from src.services.speech_service import SpeechService
from src.utils.config_loader import load_config


def main():
    """主函式"""
    print("="*60)
    print("多語言語音識別示例")
    print("="*60)

    # 載入配置
    config = load_config("config.yaml")
    
    # 建立語音服務
    speech_service = SpeechService(config)
    
    # 設定識別回呼
    def on_transcription(text):
        lang_name = speech_service.get_language_name()
        print(f"[{lang_name}] 識別結果: {text}")
    
    speech_service.on_transcription = on_transcription
    
    # 啟動服務
    speech_service.start()
    
    # 顯示支援的語言
    print("\n支援的語言:")
    for code, name in speech_service.get_supported_languages().items():
        print(f"  {code} - {name}")
    
    print("\n使用說明:")
    print("1. 對著麥克風說話，系統會自動識別")
    print("2. 輸入語言代碼切換語言:")
    print("   - 'zh' 切換到普通話")
    print("   - 'yue' 切換到粵語")
    print("   - 'en' 切換到英文")
    print("3. 輸入 'q' 退出")
    print("\n當前語言:", speech_service.get_language_name())
    print("="*60 + "\n")
    
    try:
        while True:
            # 等待用戶輸入命令
            cmd = input().strip().lower()
            
            if cmd == 'q':
                break
            elif cmd in ['zh', 'yue', 'en']:
                speech_service.set_language(cmd)
                print(f">>> 已切換到: {speech_service.get_language_name()}\n")
            elif cmd:
                print("無效的命令，請輸入 zh/yue/en 或 q")
    
    except KeyboardInterrupt:
        pass
    finally:
        speech_service.stop()
        print("\n程式已結束")


if __name__ == "__main__":
    main()
