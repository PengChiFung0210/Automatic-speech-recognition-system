# VAD + ASR 自動語音處理系統

適用於 AI VTuber 的無需按鍵、全自動語音識別系統。採用全棧架構設計，模組化、易擴展。

## 特性

- 🎤 自動語音檢測 (VAD): 無需按鍵，自動檢測何時開始/結束說話
- 🎯 即時語音識別 (ASR): 使用 Whisper 模型進行高精度識別
- 🌍 多語言支援: 支援普通話、粵語、英文，可即時切換
- ⚡ 低延遲: 使用 faster-whisper 優化性能
- 🖥️ 圖形界面: 提供直觀易用的 GUI 界面
- 🔧 模組化架構: 清晰的分層設計，易於維護和擴展
- ⚙️ 配置化: 支援 YAML/JSON 配置檔案
- 🔌 易於整合: 簡單的 API，方便整合到 VTuber 應用

## 專案結構

```
.
├── src/                      # 原始碼
│   ├── core/                 # 核心模組
│   │   ├── vad.py           # VAD 語音活動檢測
│   │   ├── asr.py           # ASR 語音識別
│   │   └── audio_stream.py  # 音訊流管理
│   ├── services/            # 服務層
│   │   ├── speech_service.py    # 語音處理服務
│   │   └── vtuber_service.py    # VTuber 業務服務
│   └── utils/               # 工具模組
│       ├── config_loader.py # 配置載入
│       └── logger.py        # 日誌工具
├── examples/                # 範例程式碼
│   ├── basic_usage.py       # 基礎使用範例
│   └── vtuber_demo.py       # VTuber 完整範例
├── tests/                   # 測試程式碼
│   ├── test_vad.py         # VAD 測試
│   └── test_audio_stream.py # 音訊流測試
├── app.py                   # 主應用入口 (命令行版本)
├── gui_app.py              # GUI 應用入口 (圖形界面版本)
├── test_gui.py             # GUI 測試腳本
├── config.yaml              # 配置檔案 (通用)
├── config_gui.yaml          # 配置檔案 (GUI 專用)
├── requirements.txt         # 依賴列表
├── download_models.py       # 模型下載工具
├── simple_test.py          # 快速測試腳本
├── run.bat                 # Windows 啟動腳本 (命令行)
├── run_gui.bat             # Windows 啟動腳本 (GUI)
├── run.sh                  # Linux/Mac 啟動腳本
├── README.md               # 專案說明
├── QUICKSTART_GUI.md       # GUI 快速啟動指南
├── GUI_GUIDE.md            # GUI 詳細使用指南
└── MULTILINGUAL_GUIDE.md   # 多語言支援指南
```

## 安裝

### 1. 安裝 Python 依賴

```bash
pip install -r requirements.txt
```

### 2. 安裝 PyAudio (Windows)

```bash
pip install pipwin
pipwin install pyaudio
```

或者從這裡下載預編譯版本: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

### 3. 可選: GPU 加速

如果有 NVIDIA GPU，可以安裝 CUDA 版本以獲得更快的識別速度:

```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 快速開始

### 方式一: GUI 圖形界面（推薦新手）

**Windows:**
```bash
run_gui.bat
```

**或直接執行:**
```bash
python gui_app.py
```

GUI 界面特性：
- 直觀的圖形界面，無需命令行操作
- 即時顯示識別結果和系統日誌
- 可視化的模型和語言選擇
- 一鍵啟動/停止服務

### 方式二: 命令行界面

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
./run.sh
```

### 方式三: 直接執行

```bash
# 1. 測試環境
python simple_test.py

# 2. 執行完整應用（命令行）
python app.py

# 3. 執行 GUI 版本
python gui_app.py

# 4. 執行範例
python examples/basic_usage.py
python examples/vtuber_demo.py
```

### 模型下載說明

**Whisper 模型會在首次執行時自動下載**，無需手動下載！

- **faster-whisper**: 模型儲存在 `~/.cache/huggingface/hub/`
- **openai-whisper**: 模型儲存在 `~/.cache/whisper/`

如果想提前下載模型：

```bash
python download_models.py
```

## 使用方法

### 0. GUI 圖形界面使用

啟動 GUI 版本後：

1. **選擇模型**: 從下拉菜單選擇 Whisper 模型（推薦使用 base）
2. **選擇語言**: 點選語言單選按鈕（普通話/粵語/English）
3. **啟動服務**: 點擊「啟動」按鈕
4. **開始說話**: 對著麥克風說話，識別結果會即時顯示
5. **切換語言**: 運行中可隨時切換語言
6. **停止服務**: 點擊「停止」按鈕

GUI 界面說明：
- **識別結果區**: 顯示所有識別到的文字，帶時間戳和語言標記
- **系統日誌區**: 顯示系統運行狀態和錯誤信息
- **狀態指示器**: 顯示當前服務狀態（未啟動/運行中/檢測到語音）

### 1. 基礎使用（程式碼整合）

```python
from src.services.speech_service import SpeechService
from src.utils.config_loader import get_default_config

# 建立語音服務
config = get_default_config()
speech_service = SpeechService(config)

# 設定識別回呼
def on_transcription(text):
    print(f"識別到: {text}")

speech_service.on_transcription = on_transcription

# 啟動服務
speech_service.start()
```

### 2. VTuber 整合

```python
from src.services.speech_service import SpeechService
from src.services.vtuber_service import VTuberService
from src.utils.config_loader import load_config

# 載入配置
config = load_config("config.yaml")

# 建立服務
speech_service = SpeechService(config)
vtuber_service = VTuberService(config.get('vtuber', {}))

# 連接服務
speech_service.on_transcription = vtuber_service.handle_user_input

# 啟動
speech_service.start()
```

### 3. 多語言切換

系統支援三種語言，可即時切換：

```python
from src.services.speech_service import SpeechService

speech_service = SpeechService(config)

# 切換到粵語
speech_service.set_language('yue')

# 切換到英文
speech_service.set_language('en')

# 切換到普通話
speech_service.set_language('zh')

# 獲取當前語言
current = speech_service.get_language_name()
print(f"當前語言: {current}")
```

在主應用中，可以直接輸入語言代碼切換：
- 輸入 `zh` - 切換到普通話
- 輸入 `yue` - 切換到粵語
- 輸入 `en` - 切換到英文

### 4. 自訂配置

編輯 `config.yaml` 檔案：

```yaml
# VAD 配置
vad:
  sample_rate: 16000
  vad_mode: 3              # 0-3, 3 最激進
  
# ASR 配置
asr:
  model_size: base         # tiny, base, small, medium, large
  language: zh             # zh (普通話), yue (粵語), en (英文)
  speech_timeout: 1.5      # 靜音逾時
  enable_language_switch: true  # 啟用語言切換
  
# VTuber 配置
vtuber:
  enable_conversation_log: true
  max_history: 20
```

## 架構說明

### 核心層 (Core)

- **VADProcessor**: 語音活動檢測，支援 WebRTC VAD 和能量檢測
- **ASREngine**: 語音識別引擎，支援 faster-whisper 和 openai-whisper
- **AudioStream**: 音訊流管理，負責音訊採集

### 服務層 (Services)

- **SpeechService**: 整合 VAD、ASR 和音訊流，提供統一的語音處理服務
- **VTuberService**: 處理 VTuber 業務邏輯，包括對話管理、動作觸發等

### 工具層 (Utils)

- **ConfigLoader**: 配置檔案載入和管理
- **Logger**: 日誌記錄工具

## 模型選擇

| 模型 | 大小 | 速度 | 精度 | 推薦場景 |
|------|------|------|------|----------|
| tiny | ~75MB | 最快 | 較低 | 即時對話、低配置 |
| base | ~150MB | 快 | 中等 | **推薦用於 VTuber** |
| small | ~500MB | 中等 | 良好 | 高品質識別 |
| medium | ~1.5GB | 慢 | 很好 | 專業應用 |
| large | ~3GB | 最慢 | 最好 | 最高精度需求 |

## 常見問題

### 1. 麥克風權限

確保應用有麥克風存取權限。

### 2. 識別延遲高

- 使用更小的模型 (tiny/base)
- 使用 faster-whisper 而不是 openai-whisper
- 啟用 GPU 加速
- 調整 `speech_timeout` 參數

### 3. 誤觸發

- 增加 `min_speech_duration`
- 調整 `vad_mode` (降低靈敏度)
- 增加 `energy_threshold`

### 4. 識別不準確

- 使用更大的模型 (small/medium)
- 確保麥克風品質良好
- 減少環境噪音

## 執行測試

```bash
# 完整測試
python simple_test.py

# 多語言示例
python examples/multilingual_demo.py

# VAD 測試
python tests/test_vad.py

# 音訊流測試
python tests/test_audio_stream.py
```

## 支援的語言

| 語言代碼 | 語言名稱 | 說明 |
|---------|---------|------|
| zh | 普通話 | 標準中文（國語） |
| yue | 粵語 | 廣東話 |
| en | English | 英文 |

## 擴展整合

### 與 AI 模型整合

```python
def generate_response(user_input):
    # 呼叫 OpenAI API
    import openai
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}]
    )
    return response.choices[0].message.content

vtuber_service.generate_response = generate_response
```

### 與 VTuber 軟體整合

```python
import websocket

def on_action_trigger(actions):
    # 透過 WebSocket 傳送到 VTuber 軟體
    ws = websocket.create_connection("ws://localhost:8080")
    ws.send(json.dumps({"actions": actions}))
    ws.close()

vtuber_service.on_action_trigger = on_action_trigger
```

## 授權

MIT License

## 貢獻

歡迎提交 Issue 和 Pull Request！
