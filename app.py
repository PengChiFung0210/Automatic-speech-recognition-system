"""
主應用入口 - 純語音識別系統
"""

import time
import threading
from src.services.speech_service import SpeechService
from src.utils.config_loader import load_config


class SpeechApp:
    """語音識別應用主類"""

    # Whisper 模型信息
    MODEL_INFO = {
        'tiny': {'size': '~75MB', 'speed': '最快', 'accuracy': '較低', 'desc': '實時對話、低配置'},
        'base': {'size': '~150MB', 'speed': '快', 'accuracy': '中等', 'desc': '推薦使用'},
        'small': {'size': '~500MB', 'speed': '中等', 'accuracy': '良好', 'desc': '高質量識別'},
        'medium': {'size': '~1.5GB', 'speed': '慢', 'accuracy': '很好', 'desc': '專業應用'},
        'large': {'size': '~3GB', 'speed': '最慢', 'accuracy': '最好', 'desc': '最高精度'}
    }

    def __init__(self, config_path="config.yaml", model_size=None):
        """
        初始化應用

        Args:
            config_path: 配置檔案路徑
            model_size: 指定模型大小 (可選)
        """
        # 載入配置
        self.config = load_config(config_path)

        # 如果指定了模型大小，覆蓋配置
        if model_size:
            if 'asr' not in self.config:
                self.config['asr'] = {}
            self.config['asr']['model_size'] = model_size

        # 初始化語音服務
        self.speech_service = SpeechService(self.config)

        # 連接回呼
        self._connect_callbacks()

    def _connect_callbacks(self):
        """連接回呼函數"""
        self.speech_service.on_transcription = self._on_transcription
        self.speech_service.on_speech_start = self._on_speech_start
        self.speech_service.on_speech_end = self._on_speech_end
        self.speech_service.on_language_change = self._on_language_change

    def _on_transcription(self, text):
        """語音識別結果回呼"""
        lang_name = self.speech_service.get_language_name()
        print(f"\n[{lang_name}] 識別結果: {text}\n")

    def _on_speech_start(self):
        """語音開始回呼"""
        pass

    def _on_speech_end(self, duration):
        """語音結束回呼"""
        pass

    def _on_language_change(self, language):
        """語言切換回呼"""
        lang_name = self.speech_service.get_language_name()
        print(f"\n>>> 語言已切換至: {lang_name}\n")

    def start(self):
        """啟動應用"""
        print("="*60)
        print("多語言語音識別系統")
        print("="*60)

        # 顯示當前使用的模型
        model_size = self.config.get('asr', {}).get('model_size', 'base')
        model_info = self.MODEL_INFO.get(model_size, {})
        print(f"\n當前模型: Whisper-{model_size}")
        if model_info:
            print(f"  大小: {model_info['size']}")
            print(f"  速度: {model_info['speed']}")
            print(f"  精度: {model_info['accuracy']}")
            print(f"  說明: {model_info['desc']}")

        # 啟動語音服務
        self.speech_service.start()

        # 顯示當前語言
        current_lang = self.speech_service.get_language_name()
        print(f"\n當前識別語言: {current_lang}")

        # 顯示支援的語言
        supported = self.speech_service.get_supported_languages()
        print("\n支援的語言:")
        for code, name in supported.items():
            print(f"  {code} - {name}")

        print("\n系統已啟動！")
        print("請對著麥克風說話，系統會自動檢測並識別")
        print("\n語言切換指令:")
        print("  輸入 'zh' 切換到普通話")
        print("  輸入 'yue' 切換到粵語")
        print("  輸入 'en' 切換到英文")
        print("  輸入 'q' 或按 Ctrl+C 退出\n")
        print("="*60 + "\n")

        # 啟動命令監聽執行緒
        self.command_thread = threading.Thread(target=self._command_listener)
        self.command_thread.daemon = True
        self.command_thread.start()

    def _command_listener(self):
        """命令監聽執行緒"""
        while True:
            try:
                cmd = input().strip().lower()
                if cmd in ['zh', 'yue', 'en']:
                    self.speech_service.set_language(cmd)
                elif cmd == 'q':
                    print("\n正在退出...")
                    import os
                    os._exit(0)
            except EOFError:
                break
            except Exception as e:
                pass

    def stop(self):
        """停止應用"""
        print("\n正在停止...")

        # 停止語音服務
        self.speech_service.stop()

        print("再見！")

    def run(self):
        """執行應用"""
        try:
            self.start()

            # 保持執行
            while True:
                time.sleep(0.1)

        except KeyboardInterrupt:
            pass
        finally:
            self.stop()


def select_model():
    """選擇 Whisper 模型"""
    print("="*60)
    print("Whisper 模型選擇")
    print("="*60)
    print("\n可用的模型:\n")

    models = ['tiny', 'base', 'small', 'medium', 'large']
    for i, model in enumerate(models, 1):
        info = SpeechApp.MODEL_INFO[model]
        print(f"{i}. {model.upper()}")
        print(f"   大小: {info['size']:<10} 速度: {info['speed']:<6} 精度: {info['accuracy']:<6}")
        print(f"   說明: {info['desc']}")
        print()

    print("="*60)

    while True:
        try:
            choice = input("\n請選擇模型 (1-5) 或直接按 Enter 使用預設 [base]: ").strip()

            if choice == "":
                return "base"

            choice_num = int(choice)
            if 1 <= choice_num <= 5:
                selected = models[choice_num - 1]
                print(f"\n已選擇: {selected.upper()}")
                return selected
            else:
                print("無效的選擇，請輸入 1-5")
        except ValueError:
            print("無效的輸入，請輸入數字 1-5")
        except KeyboardInterrupt:
            print("\n\n已取消")
            import sys
            sys.exit(0)


def main():
    """主函式"""
    # 選擇模型
    model_size = select_model()

    # 創建應用
    app = SpeechApp(model_size=model_size)
    app.run()


if __name__ == "__main__":
    main()
