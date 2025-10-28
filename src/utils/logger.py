"""
日誌工具
"""

import logging
import sys
from pathlib import Path


def setup_logger(name: str = "vad_asr", level: str = "INFO", log_file: str = None):
    """
    設定日誌記錄器

    Args:
        name: 日誌記錄器名稱
        level: 日誌級別
        log_file: 日誌檔案路徑（可選）

    Returns:
        日誌記錄器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # 清除現有處理器
    logger.handlers.clear()

    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 檔案處理器（可選）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
