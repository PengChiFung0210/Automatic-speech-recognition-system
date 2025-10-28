"""
配置載入工具
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    載入配置檔案

    Args:
        config_path: 配置檔案路徑

    Returns:
        配置字典
    """
    path = Path(config_path)

    if not path.exists():
        print(f"配置檔案不存在: {config_path}，使用預設配置")
        return get_default_config()

    try:
        if path.suffix in ['.yaml', '.yml']:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        elif path.suffix == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"不支援的配置檔案格式: {path.suffix}")
            return get_default_config()
    except Exception as e:
        print(f"載入配置檔案失敗: {e}")
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """獲取預設配置"""
    return {
        "vad": {
            "sample_rate": 16000,
            "frame_duration": 30,
            "vad_mode": 3,
            "energy_threshold": 500
        },
        "asr": {
            "model_size": "base",
            "language": "zh",
            "device": "cpu",
            "compute_type": "int8",
            "speech_timeout": 1.5,
            "min_speech_duration": 0.5,
            "model_path": None
        },
        "vtuber": {
            "enable_conversation_log": True,
            "log_file": "conversation_log.json",
            "max_history": 20
        },
        "debug": {
            "save_audio": False,
            "audio_save_path": "debug/",
            "verbose": True
        }
    }


def save_config(config: Dict[str, Any], config_path: str = "config.yaml"):
    """
    儲存配置檔案

    Args:
        config: 配置字典
        config_path: 配置檔案路徑
    """
    path = Path(config_path)

    try:
        if path.suffix in ['.yaml', '.yml']:
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        elif path.suffix == '.json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"配置已儲存到: {config_path}")
    except Exception as e:
        print(f"儲存配置檔案失敗: {e}")
