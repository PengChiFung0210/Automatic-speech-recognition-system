"""
ASR (Automatic Speech Recognition) 模組
負責語音識別
"""

import numpy as np

try:
    from faster_whisper import WhisperModel
    HAS_FASTER_WHISPER = True
except ImportError:
    HAS_FASTER_WHISPER = False

try:
    import whisper
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False


class ASREngine:
    """語音識別引擎"""

    # 支援的語言
    SUPPORTED_LANGUAGES = {
        'zh': '普通話',
        'yue': '粵語',
        'en': 'English'
    }

    def __init__(self,
                 model_size="base",
                 language="zh",
                 device="cpu",
                 compute_type="int8",
                 model_path=None):
        """
        初始化 ASR 引擎

        Args:
            model_size: 模型大小 (tiny, base, small, medium, large)
            language: 語言代碼 (zh, yue, en)
            device: 裝置 (cpu, cuda)
            compute_type: 計算類型 (int8, float16, float32)
            model_path: 本地模型路徑（可選）
        """
        self.language = language
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type

        print(f"正在載入 Whisper 模型: {model_size}...")
        print("提示: 首次執行會自動下載模型，請耐心等待...")

        if HAS_FASTER_WHISPER:
            self._init_faster_whisper(model_size, device, compute_type, model_path)
        elif HAS_WHISPER:
            self._init_openai_whisper(model_size, model_path)
        else:
            raise RuntimeError("未安裝 Whisper 模型，請安裝 faster-whisper 或 openai-whisper")

        print("模型載入完成！")

    def _init_faster_whisper(self, model_size, device, compute_type, model_path):
        """初始化 faster-whisper"""
        if model_path:
            print(f"使用本地模型: {model_path}")
            self.model = WhisperModel(model_path, device=device, compute_type=compute_type)
        else:
            print(f"使用線上模型: {model_size} (首次會自動下載)")
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.use_faster_whisper = True

    def _init_openai_whisper(self, model_size, model_path):
        """初始化 openai-whisper"""
        print(f"使用 openai-whisper (首次會自動下載)")
        self.model = whisper.load_model(model_size, download_root=model_path)
        self.use_faster_whisper = False

    def transcribe(self, audio_data):
        """
        執行語音識別

        Args:
            audio_data: 音訊資料 (numpy array, float32, [-1, 1])

        Returns:
            str: 識別文字
        """
        try:
            if self.use_faster_whisper:
                return self._transcribe_faster_whisper(audio_data)
            else:
                return self._transcribe_openai_whisper(audio_data)
        except Exception as e:
            print(f"識別失敗: {e}")
            return ""

    def _transcribe_faster_whisper(self, audio_data):
        """使用 faster-whisper 識別"""
        segments, info = self.model.transcribe(
            audio_data,
            language=self.language,
            beam_size=5,
            vad_filter=True
        )
        text = " ".join([segment.text for segment in segments]).strip()
        return text

    def _transcribe_openai_whisper(self, audio_data):
        """使用 openai-whisper 識別"""
        result = self.model.transcribe(
            audio_data,
            language=self.language,
            fp16=False
        )
        return result["text"].strip()

    def set_language(self, language):
        """
        切換識別語言

        Args:
            language: 語言代碼 (zh, yue, en)
        """
        if language not in self.SUPPORTED_LANGUAGES:
            print(f"不支援的語言: {language}")
            return False
        
        self.language = language
        lang_name = self.SUPPORTED_LANGUAGES[language]
        print(f"已切換到 {lang_name} 識別模式")
        return True

    def get_current_language(self):
        """獲取當前語言"""
        return self.language

    def get_language_name(self):
        """獲取當前語言名稱"""
        return self.SUPPORTED_LANGUAGES.get(self.language, self.language)
