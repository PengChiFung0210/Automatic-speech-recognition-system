"""
多語言語音識別系統 - GUI 版本
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
from datetime import datetime
from src.services.speech_service import SpeechService
from src.utils.config_loader import load_config


class SpeechRecognitionGUI:
    """語音識別 GUI 應用"""
    
    # Whisper 模型信息
    MODEL_INFO = {
        'tiny': {'size': '~75MB', 'speed': '最快', 'accuracy': '較低'},
        'base': {'size': '~150MB', 'speed': '快', 'accuracy': '中等'},
        'small': {'size': '~500MB', 'speed': '中等', 'accuracy': '良好'},
        'medium': {'size': '~1.5GB', 'speed': '慢', 'accuracy': '很好'},
        'large': {'size': '~3GB', 'speed': '最慢', 'accuracy': '最好'}
    }
    
    # 語言信息
    LANGUAGES = {
        'zh': '普通話',
        'yue': '粵語',
        'en': 'English'
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("多語言語音識別系統")
        self.root.geometry("900x650")
        
        # 设置窗口图标（如果有的话）
        try:
            # self.root.iconbitmap('icon.ico')
            pass
        except:
            pass
        
        # 狀態變數
        self.is_running = False
        self.speech_service = None
        self.config = None
        self.message_queue = queue.Queue()
        self.recognition_count = 0
        
        # 建立選單列
        self._create_menu()
        
        # 建立介面
        self._create_widgets()
        
        # 載入配置
        self._load_config()
        
        # 啟動訊息處理
        self._process_queue()
        
    def _create_menu(self):
        """建立選單列"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 檔案選單
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="檔案", menu=file_menu)
        file_menu.add_command(label="重新載入配置", command=self._reload_config)
        file_menu.add_separator()
        file_menu.add_command(label="結束", command=self.on_closing)
        
        # 編輯選單
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="編輯", menu=edit_menu)
        edit_menu.add_command(label="清空識別結果", command=self._clear_results)
        edit_menu.add_command(label="複製全部結果", command=self._copy_all_results)
        edit_menu.add_separator()
        edit_menu.add_command(label="清空日誌", command=self._clear_logs)
        
        # 說明選單
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="說明", menu=help_menu)
        help_menu.add_command(label="使用說明", command=self._show_help)
        help_menu.add_command(label="關於", command=self._show_about)
    
    def _create_widgets(self):
        """建立介面元件"""
        # 頂部控制面板
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # 模型選擇
        ttk.Label(control_frame, text="模型:").grid(row=0, column=0, padx=5)
        self.model_var = tk.StringVar(value='base')
        model_combo = ttk.Combobox(control_frame, textvariable=self.model_var, 
                                   values=list(self.MODEL_INFO.keys()), 
                                   state='readonly', width=10)
        model_combo.grid(row=0, column=1, padx=5)
        model_combo.bind('<<ComboboxSelected>>', self._on_model_change)
        
        # 模型資訊標籤
        self.model_info_label = ttk.Label(control_frame, text="")
        self.model_info_label.grid(row=0, column=2, padx=10)
        self._update_model_info()
        
        # 語言選擇
        ttk.Label(control_frame, text="語言:").grid(row=0, column=3, padx=5)
        self.language_var = tk.StringVar(value='zh')
        language_frame = ttk.Frame(control_frame)
        language_frame.grid(row=0, column=4, padx=5)
        
        for code, name in self.LANGUAGES.items():
            ttk.Radiobutton(language_frame, text=name, value=code, 
                          variable=self.language_var,
                          command=self._on_language_change).pack(side=tk.LEFT, padx=3)
        
        # 啟動/停止按鈕
        self.start_button = ttk.Button(control_frame, text="啟動", 
                                       command=self._toggle_service, width=10)
        self.start_button.grid(row=0, column=5, padx=10)
        
        # 狀態指示器
        self.status_label = ttk.Label(control_frame, text="● 未啟動", 
                                     foreground="gray")
        self.status_label.grid(row=0, column=6, padx=5)
        
        # 分隔線
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # 中間內容區域
        content_frame = ttk.Frame(self.root, padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 識別結果顯示區
        result_label_frame = ttk.LabelFrame(content_frame, text="識別結果", padding="5")
        result_label_frame.pack(fill=tk.BOTH, expand=True)
        
        # 新增清空和複製按鈕
        result_button_frame = ttk.Frame(result_label_frame)
        result_button_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(result_button_frame, text="清空結果", 
                  command=self._clear_results, width=10).pack(side=tk.RIGHT)
        ttk.Button(result_button_frame, text="複製全部", 
                  command=self._copy_all_results, width=10).pack(side=tk.RIGHT, padx=5)
        
        self.result_text = scrolledtext.ScrolledText(result_label_frame, 
                                                     wrap=tk.WORD, 
                                                     height=15,
                                                     font=('Microsoft JhengHei UI', 10))
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 日誌顯示區
        log_label_frame = ttk.LabelFrame(content_frame, text="系統日誌", padding="5")
        log_label_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_label_frame, 
                                                  wrap=tk.WORD, 
                                                  height=8,
                                                  font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 底部資訊列
        info_frame = ttk.Frame(self.root, padding="5")
        info_frame.pack(fill=tk.X)
        
        self.info_label = ttk.Label(info_frame, 
                                    text="請選擇模型和語言，然後點擊「啟動」開始識別",
                                    foreground="blue")
        self.info_label.pack(side=tk.LEFT)
        
        # 統計資訊
        self.stats_label = ttk.Label(info_frame, text="識別次數: 0")
        self.stats_label.pack(side=tk.RIGHT, padx=10)
        
    def _load_config(self):
        """載入配置"""
        try:
            # 優先載入 GUI 專用配置，如果不存在則使用預設配置
            import os
            if os.path.exists("config_gui.yaml"):
                self.config = load_config("config_gui.yaml")
                self._log("已載入 GUI 專用配置")
            else:
                self.config = load_config("config.yaml")
                self._log("已載入預設配置")
            
            # 從配置中讀取預設值
            if 'asr' in self.config:
                model = self.config['asr'].get('model_size', 'base')
                self.model_var.set(model)
                self._update_model_info()
                
                lang = self.config['asr'].get('language', 'zh')
                self.language_var.set(lang)
            
            # 套用 GUI 配置
            if 'gui' in self.config:
                gui_config = self.config['gui']
                width = gui_config.get('window_width', 900)
                height = gui_config.get('window_height', 650)
                self.root.geometry(f"{width}x{height}")
                
        except Exception as e:
            self._log(f"配置載入失敗: {e}", level="ERROR")
            messagebox.showerror("錯誤", f"配置載入失敗: {e}")
    
    def _update_model_info(self):
        """更新模型資訊顯示"""
        model = self.model_var.get()
        info = self.MODEL_INFO.get(model, {})
        text = f"大小: {info.get('size', '')} | 速度: {info.get('speed', '')} | 精度: {info.get('accuracy', '')}"
        self.model_info_label.config(text=text)
    
    def _on_model_change(self, event=None):
        """模型改變事件"""
        self._update_model_info()
        if self.is_running:
            self._log("模型已更改，請重啟服務以套用變更", level="WARNING")
    
    def _on_language_change(self):
        """語言改變事件"""
        if self.is_running and self.speech_service:
            lang_code = self.language_var.get()
            lang_name = self.LANGUAGES.get(lang_code, lang_code)
            self.speech_service.set_language(lang_code)
            self._log(f"語言已切換至: {lang_name}")
    
    def _toggle_service(self):
        """切換服務狀態"""
        if self.is_running:
            self._stop_service()
        else:
            self._start_service()
    
    def _start_service(self):
        """啟動語音識別服務"""
        try:
            self._log("正在啟動語音識別服務...")
            self.info_label.config(text="正在初始化，請稍候...")
            
            # 更新配置
            model = self.model_var.get()
            lang = self.language_var.get()
            
            if 'asr' not in self.config:
                self.config['asr'] = {}
            self.config['asr']['model_size'] = model
            self.config['asr']['language'] = lang
            
            # 在背景執行緒中初始化服務
            def init_service():
                try:
                    self.speech_service = SpeechService(self.config)
                    
                    # 連接回呼
                    self.speech_service.on_transcription = self._on_transcription
                    self.speech_service.on_speech_start = self._on_speech_start
                    self.speech_service.on_speech_end = self._on_speech_end
                    self.speech_service.on_language_change = self._on_language_change_callback
                    
                    # 啟動服務
                    self.speech_service.start()
                    
                    self.message_queue.put(('service_started', None))
                    
                except Exception as e:
                    self.message_queue.put(('service_error', str(e)))
            
            thread = threading.Thread(target=init_service, daemon=True)
            thread.start()
            
        except Exception as e:
            self._log(f"啟動失敗: {e}", level="ERROR")
            messagebox.showerror("錯誤", f"啟動失敗: {e}")
    
    def _stop_service(self):
        """停止語音識別服務"""
        try:
            self._log("正在停止語音識別服務...")
            
            if self.speech_service:
                self.speech_service.stop()
                self.speech_service = None
            
            self.is_running = False
            self.start_button.config(text="啟動")
            self.status_label.config(text="● 未啟動", foreground="gray")
            self.info_label.config(text="服務已停止")
            
            self._log("服務已停止")
            
        except Exception as e:
            self._log(f"停止失敗: {e}", level="ERROR")
    
    def _on_transcription(self, text):
        """识别结果回调"""
        self.message_queue.put(('transcription', text))
    
    def _on_speech_start(self):
        """语音开始回调"""
        self.message_queue.put(('speech_start', None))
    
    def _on_speech_end(self, duration):
        """语音结束回调"""
        self.message_queue.put(('speech_end', duration))
    
    def _on_language_change_callback(self, language):
        """语言切换回调"""
        self.message_queue.put(('language_change', language))
    
    def _process_queue(self):
        """處理訊息佇列"""
        try:
            while True:
                msg_type, data = self.message_queue.get_nowait()
                
                if msg_type == 'service_started':
                    self.is_running = True
                    self.start_button.config(text="停止")
                    self.status_label.config(text="● 運行中", foreground="green")
                    lang_name = self.LANGUAGES.get(self.language_var.get(), '')
                    self.info_label.config(text=f"服務運行中 | 當前語言: {lang_name} | 請對著麥克風說話")
                    self._log("服務啟動成功，開始監聽...")
                    
                elif msg_type == 'service_error':
                    self.info_label.config(text="啟動失敗")
                    self._log(f"服務啟動失敗: {data}", level="ERROR")
                    messagebox.showerror("錯誤", f"服務啟動失敗: {data}")
                    
                elif msg_type == 'transcription':
                    lang_name = self.LANGUAGES.get(self.language_var.get(), '')
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.result_text.insert(tk.END, f"[{timestamp}] [{lang_name}] {data}\n")
                    self.result_text.see(tk.END)
                    self.recognition_count += 1
                    self._update_stats()
                    
                elif msg_type == 'speech_start':
                    self.status_label.config(text="● 檢測到語音", foreground="orange")
                    
                elif msg_type == 'speech_end':
                    self.status_label.config(text="● 運行中", foreground="green")
                    
                elif msg_type == 'language_change':
                    lang_name = self.LANGUAGES.get(data, data)
                    self._log(f"語言已切換至: {lang_name}")
                    
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._process_queue)
    
    def _log(self, message, level="INFO"):
        """記錄日誌"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # 根據級別設定顏色
        if level == "ERROR":
            # 為最後一行設定紅色
            last_line = self.log_text.index("end-1c linestart")
            self.log_text.tag_add("error", last_line, "end-1c")
            self.log_text.tag_config("error", foreground="red")
        elif level == "WARNING":
            last_line = self.log_text.index("end-1c linestart")
            self.log_text.tag_add("warning", last_line, "end-1c")
            self.log_text.tag_config("warning", foreground="orange")
    
    def _clear_results(self):
        """清空識別結果"""
        if messagebox.askyesno("確認", "確定要清空所有識別結果嗎？"):
            self.result_text.delete(1.0, tk.END)
            self.recognition_count = 0
            self._update_stats()
            self._log("識別結果已清空")
    
    def _copy_all_results(self):
        """複製所有識別結果到剪貼簿"""
        try:
            content = self.result_text.get(1.0, tk.END).strip()
            if content:
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                self._log("已複製所有識別結果到剪貼簿")
                messagebox.showinfo("成功", "已複製到剪貼簿")
            else:
                messagebox.showwarning("提示", "沒有可複製的內容")
        except Exception as e:
            self._log(f"複製失敗: {e}", level="ERROR")
            messagebox.showerror("錯誤", f"複製失敗: {e}")
    
    def _update_stats(self):
        """更新統計資訊"""
        self.stats_label.config(text=f"識別次數: {self.recognition_count}")
    
    def _reload_config(self):
        """重新載入配置"""
        if self.is_running:
            messagebox.showwarning("警告", "請先停止服務再重新載入配置")
            return
        
        self._load_config()
        messagebox.showinfo("成功", "配置已重新載入")
    
    def _clear_logs(self):
        """清空日誌"""
        if messagebox.askyesno("確認", "確定要清空所有日誌嗎？"):
            self.log_text.delete(1.0, tk.END)
            self._log("日誌已清空")
    
    def _show_help(self):
        """顯示說明資訊"""
        help_text = """
多語言語音識別系統 - 使用說明

1. 選擇模型
   - tiny: 最快，適合低配置
   - base: 推薦使用，速度和精度平衡
   - small/medium/large: 更高精度，需要更多資源

2. 選擇語言
   - 普通話 (zh): 標準中文
   - 粵語 (yue): 廣東話
   - English (en): 英文
   - 可在運行中隨時切換

3. 啟動服務
   - 點擊「啟動」按鈕
   - 首次使用會下載模型，請耐心等待
   - 看到「服務啟動成功」後即可使用

4. 開始識別
   - 對著麥克風說話
   - 識別結果會即時顯示
   - 可以隨時切換語言

5. 常見問題
   - 無法識別：檢查麥克風權限和音量
   - 延遲高：使用更小的模型或啟用 GPU
   - 識別不準：使用更大的模型

詳細文件請查看 README.md
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("使用說明")
        help_window.geometry("500x400")
        
        text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, 
                                        font=('Microsoft JhengHei UI', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(1.0, help_text)
        text.config(state=tk.DISABLED)
        
        ttk.Button(help_window, text="關閉", 
                  command=help_window.destroy).pack(pady=10)
    
    def _show_about(self):
        """顯示關於資訊"""
        about_text = """
多語言語音識別系統
版本: 1.0.0

基於 Whisper 的自動語音識別系統
支援普通話、粵語、英文

特性:
• 自動語音檢測 (VAD)
• 即時語音識別 (ASR)
• 多語言支援
• 低延遲優化

技術棧:
• faster-whisper
• WebRTC VAD
• PyAudio
• tkinter

開源專案，歡迎貢獻！
        """
        messagebox.showinfo("關於", about_text)
    
    def on_closing(self):
        """視窗關閉事件"""
        if self.is_running:
            if messagebox.askokcancel("結束", "服務正在運行，確定要結束嗎？"):
                self._stop_service()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    """主函式"""
    root = tk.Tk()
    app = SpeechRecognitionGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
