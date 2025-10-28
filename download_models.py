"""
預下載 Whisper 模型
如果網路不穩定，可以先執行此腳本下載模型
"""

import os
import sys

def download_faster_whisper_model(model_size="base"):
    """下載 faster-whisper 模型"""
    try:
        from faster_whisper import WhisperModel
        
        print(f"開始下載 faster-whisper 模型: {model_size}")
        print("模型將儲存到: ~/.cache/huggingface/hub/")
        print("請耐心等待...\n")
        
        # 載入模型會自動下載
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
        print(f"\n模型 {model_size} 下載完成！")
        return True
        
    except ImportError:
        print("未安裝 faster-whisper")
        print("請執行: pip install faster-whisper")
        return False
    except Exception as e:
        print(f"下載失敗: {e}")
        return False


def download_openai_whisper_model(model_size="base"):
    """下載 openai-whisper 模型"""
    try:
        import whisper
        
        print(f"開始下載 openai-whisper 模型: {model_size}")
        print("模型將儲存到: ~/.cache/whisper/")
        print("請耐心等待...\n")
        
        # 載入模型會自動下載
        model = whisper.load_model(model_size)
        
        print(f"\n模型 {model_size} 下載完成！")
        return True
        
    except ImportError:
        print("未安裝 openai-whisper")
        print("請執行: pip install openai-whisper")
        return False
    except Exception as e:
        print(f"下載失敗: {e}")
        return False


def main():
    """主函式"""
    print("="*60)
    print("Whisper 模型下載工具")
    print("="*60)
    
    print("\n可用模型:")
    models = {
        "1": ("tiny", "~75MB", "最快，適合即時對話"),
        "2": ("base", "~150MB", "推薦，速度和精度平衡"),
        "3": ("small", "~500MB", "較好精度"),
        "4": ("medium", "~1.5GB", "高精度"),
        "5": ("large", "~3GB", "最高精度"),
    }
    
    for key, (name, size, desc) in models.items():
        print(f"  [{key}] {name:8s} - {size:8s} - {desc}")
    
    print("\n選擇要下載的模型 (預設: 2):")
    choice = input("請輸入數字: ").strip() or "2"
    
    if choice not in models:
        print("無效選擇")
        sys.exit(1)
    
    model_size = models[choice][0]
    
    print("\n選擇下載方式:")
    print("  [1] faster-whisper (推薦，更快)")
    print("  [2] openai-whisper (相容性好)")
    
    method = input("請輸入數字 (預設: 1): ").strip() or "1"
    
    print("\n" + "="*60)
    
    if method == "1":
        success = download_faster_whisper_model(model_size)
    elif method == "2":
        success = download_openai_whisper_model(model_size)
    else:
        print("無效選擇")
        sys.exit(1)
    
    if success:
        print("\n" + "="*60)
        print("下載完成！現在可以執行:")
        print("  python app.py")
        print("  python examples/basic_usage.py")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("下載失敗，請檢查網路連線或依賴安裝")
        print("="*60)


if __name__ == "__main__":
    main()
