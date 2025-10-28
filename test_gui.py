"""
GUI 测试脚本 - 验证 GUI 是否能正常启动
"""

import sys

def test_imports():
    """测试所有必要的导入"""
    print("测试导入模块...")
    
    try:
        import tkinter as tk
        print("✓ tkinter 导入成功")
    except ImportError as e:
        print(f"✗ tkinter 导入失败: {e}")
        return False
    
    try:
        from tkinter import ttk, scrolledtext, messagebox
        print("✓ tkinter 子模块导入成功")
    except ImportError as e:
        print(f"✗ tkinter 子模块导入失败: {e}")
        return False
    
    try:
        from src.services.speech_service import SpeechService
        print("✓ SpeechService 导入成功")
    except ImportError as e:
        print(f"✗ SpeechService 导入失败: {e}")
        return False
    
    try:
        from src.utils.config_loader import load_config
        print("✓ config_loader 导入成功")
    except ImportError as e:
        print(f"✗ config_loader 导入失败: {e}")
        return False
    
    return True


def test_gui_creation():
    """测试 GUI 创建"""
    print("\n测试 GUI 创建...")
    
    try:
        import tkinter as tk
        from gui_app import SpeechRecognitionGUI
        
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        app = SpeechRecognitionGUI(root)
        print("✓ GUI 创建成功")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ GUI 创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("="*60)
    print("GUI 测试")
    print("="*60)
    print()
    
    # 测试导入
    if not test_imports():
        print("\n导入测试失败！")
        sys.exit(1)
    
    # 测试 GUI 创建
    if not test_gui_creation():
        print("\nGUI 创建测试失败！")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("所有测试通过！")
    print("="*60)
    print("\n可以运行 GUI 应用:")
    print("  python gui_app.py")
    print("  或")
    print("  run_gui.bat")


if __name__ == "__main__":
    main()
