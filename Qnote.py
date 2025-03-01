import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import markdown
import os
import re
import webbrowser
class EnhancedMarkdownEditor:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Qnote")
        self.root.geometry("1400x900")
        self.current_file = None
        self.theme_mode = "light"
        self.setup_ui()
        self.modified = False
        self.create_menu()
        self.create_toolbar()
        self.create_statusbar()
        self.bind_shortcuts()
        self.set_theme("light")
        self.setup_highlight_tags()
        self.setup_autosave()
    
        #self.open_web_about()
    
    def setup_ui(self):

        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(expand=True, fill='both', padx=5, pady=5)

        self.editor_frame = ttk.Frame(main_paned)
        self.text_area = scrolledtext.ScrolledText(
            self.editor_frame,
            wrap=tk.WORD,
            font=('Consolas', 12),
            undo=True,
            autoseparators=True,
            maxundo=-1
        )
        self.text_area.pack(expand=True, fill='both')
        main_paned.add(self.editor_frame, weight=2)

       
        self.preview_frame = ttk.Frame(main_paned)
        self.preview_paned = ttk.PanedWindow(self.preview_frame, orient=tk.VERTICAL)
        
    
        
     
        self.outline_tree = ttk.Treeview(self.preview_paned)
        self.preview_paned.add(self.outline_tree, weight=1)
        
        self.preview_paned.pack(expand=True, fill='both')
        main_paned.add(self.preview_frame, weight=3)

       
        self.text_area.bind('<KeyRelease>', self.on_content_changed)
    def helpus(self):
        webbrowser.open("https://github.com/Reoame/Qnote/issues")
    def open_web_about(self):
        webbrowser.open("https://reoame.github.io/Mypage/about.html")
    def create_menu(self):
    
        menu_bar = tk.Menu(self.root)
       
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="新建", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="打开", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="保存", command=self.save_file, accelerator="Ctrl+S")
        
        file_menu.add_command(label="另存为", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="导出HTML", command=self.export_html)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        file_menu.add_command(label="给我们提建议", command=self.helpus)
        file_menu.add_command(label="关于", command=self.open_web_about)
        menu_bar.add_cascade(label="文件", menu=file_menu)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="撤销", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="重做", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="查找替换", command=self.show_search_dialog)
        menu_bar.add_cascade(label="编辑", menu=edit_menu)

        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="切换主题", command=self.toggle_theme)
        view_menu.add_checkbutton(label="语法高亮", variable=tk.BooleanVar(value=True))
        menu_bar.add_cascade(label="视图", menu=view_menu)
        
        

        self.root.config(menu=menu_bar)

    def create_toolbar(self):

        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=2, pady=2)

        btn_data = [
            ("📄", self.new_file),
            ("📂", self.open_file),
            ("💾", self.save_file),
            ("🔍", self.show_search_dialog),
            ("#", lambda: self.insert_header()),
            ("B", lambda: self.wrap_selection("**")),
            ("I", lambda: self.wrap_selection("*")),
            ("🔗", self.insert_link),
            ("🖼️", self.insert_image),
            ("Σ", lambda: self.insert_math()),
        ]

        for text, cmd in btn_data:
            btn = ttk.Button(toolbar, text=text, command=cmd)
            btn.pack(side=tk.LEFT, padx=2)

    def create_statusbar(self):

        self.status_bar = ttk.Label(
            self.root,
            text="就绪 | 行数: 1 | 列数: 1 | 字数: 0",
            relief=tk.SUNKEN
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_highlight_tags(self):
   
        self.text_area.tag_configure("header", foreground="#2c3e50", font=('Consolas', 14, 'bold'))
        self.text_area.tag_configure("bold", font=('Consolas', 12, 'bold'))
        self.text_area.tag_configure("italic", font=('Consolas', 12, 'italic'))
        self.text_area.tag_configure("code", background="#f0f0f0")
        self.text_area.tag_configure("link", foreground="#3498db")
        self.text_area.tag_configure("math", foreground="#e74c3c")

    def on_content_changed(self, event=None):

        self.update_highlighting()
        self.update_preview()
        self.update_outline()
        self.update_status()

    def update_highlighting(self):

        for tag in ["header", "bold", "italic", "code", "link", "math"]:
            self.text_area.tag_remove(tag, "1.0", "end")

        content = self.text_area.get("1.0", "end")
       
        for match in re.finditer(r'^(#{1,6})\s+(.+)$', content, re.M):
            start = f"1.0 + {match.start()}c"
            end = f"1.0 + {match.end()}c"
            self.text_area.tag_add("header", start, end)
        for match in re.finditer(r'(\*|_)(.*?)\1', content):
            start = f"1.0 + {match.start()}c"
            end = f"1.0 + {match.end()}c"
            self.text_area.tag_add("italic", start, end)

        for match in re.finditer(r'`(.*?)`', content):
            start = f"1.0 + {match.start()}c"
            end = f"1.0 + {match.end()}c"
            self.text_area.tag_add("code", start, end)
        for match in re.finditer(r'\*\*(.*?)\*\*', content):
            self.text_area.tag_add("bold", f"1.0 + {match.start()}c", f"1.0 + {match.end()}c")
        

        for match in re.finditer(r'\$(.*?)\$', content):
            self.text_area.tag_add("math", f"1.0 + {match.start()}c", f"1.0 + {match.end()}c")

    def update_preview(self):
        content = self.text_area.get("1.0", "end-1c")
        html = markdown.markdown(content, extensions=['tables', 'fenced_code'])
        
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>预览</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 
                       'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: {self.get_theme_color('bg')};
            color: {self.get_theme_color('fg')};
        }}
        pre {{ 
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        code {{ 
            background: #f0f0f0; 
            padding: 2px 4px; 
            font-family: 'Consolas', monospace;
        }}
        table {{
            border-collapse: collapse; 
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{ 
            border: 1px solid #ddd; 
            padding: 8px;
            text-align: left;
        }}
        th {{ 
            background: #f5f5f5;
            font-weight: bold;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            margin: 1.5em 0;
            padding: 0.5em 1em;
            color: #666;
        }}
        .math {{ color: #e74c3c; }}
    </style>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async
            src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
    </script>
</head>
<body>
    {html}
</body>
</html>"""

    

    

    def get_theme_color(self, element):
        themes = {
            "light": {"bg": "#ffffff", "fg": "#333333"},
            "dark": {"bg": "#2d2d2d", "fg": "#cccccc"}
        }
        return themes[self.theme_mode][element]

    def update_outline(self):
      
        self.outline_tree.delete(*self.outline_tree.get_children())
        content = self.text_area.get("1.0", "end-1c")
        headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        
        for level, title in headings:
            level = len(level)
            self.outline_tree.insert("", "end", text=title, tags=[f"h{level}"])

    def set_theme(self, theme):
      
        themes = {
            "light": {
                "bg": "#ffffff",
                "fg": "#333333",
                "text_bg": "#ffffff",
                "status_bg": "#f0f0f0"
            },
            "dark": {
                "bg": "#2d2d2d",
                "fg": "#cccccc",
                "text_bg": "#1e1e1e",
                "status_bg": "#3c3c3c"
            }
        }
        t = themes[theme]
        self.text_area.config(bg=t['text_bg'], fg=t['fg'])
        self.status_bar.config(background=t['status_bg'], foreground=t['fg'])
        self.root.config(bg=t['bg'])
        self.theme_mode = theme
        self.update_preview()

    def new_file(self):
      
        self.text_area.delete("1.0", "end")
        self.current_file = None
        self.update_status()

    def open_file(self):
  
        file_path = filedialog.askopenfilename(
            filetypes=[("Markdown文件", "*.md"), ("所有文件", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
                self.current_file = file_path
                self.update_status()
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件: {str(e)}")

    def save_file(self):

        if self.current_file:
            try:
                content = self.text_area.get("1.0", "end-1c")
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(content)
                self.status_bar.config(text="文件保存成功")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
        else:
            self.save_as_file()

    def save_as_file(self):

        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown文件", "*.md"), ("所有文件", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            self.save_file()
    def export_html(self):
    # 弹出一次保存对话框获取文件路径
        file_path = filedialog.asksaveasfilename(
        defaultextension=".html",
        filetypes=[("HTML文件", "*.html")]
    )
        if not file_path:  # 用户取消保存
            return
    
        content = self.text_area.get("1.0", "end-1c")
        html = markdown.markdown(content, extensions=['tables', 'fenced_code'])
    
    # 提取文件名用于标题
        file_name = os.path.splitext(os.path.basename(file_path))[0] 
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{file_name}</title>

    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{self.get_preview_styles()}
    </style>
</head>
<body>
    <article>
        <div class="post-content">
            {html}
        </div>
    </article>
</body>
</html>"""
    
    # 写入文件并提示
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(full_html)
            messagebox.showinfo("导出成功", f"HTML文件已保存到:\n{file_path}")
        except Exception as e:
            messagebox.showerror("导出失败", f"保存文件时出错:\n{str(e)}")
    def get_preview_styles(self):
     
        return """
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 
                       'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        pre { 
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        code { 
            background: #f0f0f0; 
            padding: 2px 4px; 
            font-family: 'Consolas', monospace;
        }
        table {
            border-collapse: collapse; 
            width: 100%;
            margin: 15px 0;
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 8px;
            text-align: left;
        }
        th { 
            background: #f5f5f5;
            font-weight: bold;
        }
        blockquote {
            border-left: 4px solid #ddd;
            margin: 1.5em 0;
            padding: 0.5em 1em;
            color: #666;
        }
        .math { color: #e74c3c; }
        a {
        text-decoration: none;
        color: #2c3e50;

        }
        a:hover {
  color: #3498db; /* 悬停时的颜色，例如浅蓝色 */
  text-decoration: underline; /* 可选：添加下划线 */
}
        """

    

    def wrap_full_html(self, content):
 
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>预览</title>
            <style>
                {self.get_preview_styles()}
            </style>
        </head>
        <body>
            {content}
            
        </body>
        </html>
        """

    def toggle_theme(self):
        self.set_theme("dark" if self.theme_mode == "light" else "light")

    def update_status(self):
        text = self.text_area.get("1.0", "end-1c")
        char_count = len(text)
        words = len(text.split())
        lines = text.count('\n') + 1
        current_line, current_col = self.text_area.index(tk.INSERT).split('.')
        status_text = f"状态: {'已保存' if self.current_file else '未保存'} | 行: {current_line} | 列: {current_col} | 字符数: {char_count} | 单词数: {words}"
        self.status_bar.config(text=status_text)

    def undo(self):
      
        self.text_area.edit_undo()

    def redo(self):
    
        self.text_area.edit_redo()

    def wrap_selection(self, symbol):
  
        self.text_area.insert(tk.INSERT, f"{symbol}{symbol}")
        self.text_area.mark_set(tk.INSERT, f"insert-{len(symbol)}c")

    def insert_header(self):

        self.text_area.insert(tk.INSERT, "# ")
        self.text_area.mark_set(tk.INSERT, "insert-2c")

    def insert_link(self):
 
        self.text_area.insert(tk.INSERT, "[显示文本](http://)")
        self.text_area.mark_set(tk.INSERT, "insert-9c")

    def insert_image(self):
   
        self.text_area.insert(tk.INSERT, "![描述](图片地址)")
        self.text_area.mark_set(tk.INSERT, "insert-9c")

    def insert_math(self):
      
        self.text_area.insert(tk.INSERT, "$公式$")
        self.text_area.mark_set(tk.INSERT, "insert-1c")

    def show_search_dialog(self):
       
        search_win = tk.Toplevel(self.root)
        search_win.resizable(False, False)
        search_win.title("查找替换")
        
        ttk.Label(search_win, text="查找:").grid(row=0, column=0, padx=5, pady=5)
        self.search_entry = ttk.Entry(search_win, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(search_win, text="替换为:").grid(row=1, column=0, padx=5, pady=5)
        self.replace_entry = ttk.Entry(search_win, width=30)
        self.replace_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(search_win, text="查找下一个", command=self.find_next).grid(row=0, column=2, padx=5)
        ttk.Button(search_win, text="替换", command=self.replace_text).grid(row=1, column=2, padx=5)
        ttk.Button(search_win, text="全部替换", command=self.replace_all).grid(row=2, column=2, padx=5)
    def togithub(self):
        g = tk.Toplevel(self.root)
        g.resizable(False, False)
        g.title("上传到GitHub")
        ttk.Label(g, text="请输入GitHub仓库地址:").grid(row=0, column=0, padx=5, pady=5)
        self.github_entry = ttk.Entry(g, width=30)
        self.github_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(g, text="上传", command=self.upload_to_github).grid(row=0, column=2, padx=5)
    
    def find_next(self):
        
        search_term = self.search_entry.get()
        if search_term:
            start_pos = self.text_area.search(
                search_term, 
                tk.INSERT, 
                nocase=True, 
                stopindex=tk.END
            )
            if start_pos:
                end_pos = f"{start_pos}+{len(search_term)}c"
                self.text_area.tag_remove("search", "1.0", tk.END)
                self.text_area.tag_add("search", start_pos, end_pos)
                self.text_area.tag_config("search", background="yellow")
                self.text_area.mark_set(tk.INSERT, end_pos)
                self.text_area.see(tk.INSERT)

    def replace_text(self):
        
        search_term = self.search_entry.get()
        replace_term = self.replace_entry.get()
        if search_term and replace_term:
            start_pos = self.text_area.search(
                search_term, 
                tk.INSERT, 
                nocase=True, 
                stopindex=tk.END
            )
            if start_pos:
                end_pos = f"{start_pos}+{len(search_term)}c"
                self.text_area.delete(start_pos, end_pos)
                self.text_area.insert(start_pos, replace_term)
                self.find_next()

    def replace_all(self):
        search_term = self.search_entry.get()
        replace_term = self.replace_entry.get()
        if search_term and replace_term:
            content = self.text_area.get("1.0", tk.END)
            new_content = content.replace(search_term, replace_term)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", new_content)

    def setup_autosave(self):
     
        self.root.after(30000, self.autosave)
    def autosave(self):
        
        if self.current_file:
            self.save_file()
        self.root.after(30000, self.autosave)
    def reopen_last_file(self, event=None):
        """重新打开最后一次编辑的文件"""
        if self.current_file:
            if not os.path.exists(self.current_file):
                messagebox.showerror("错误", f"文件不存在: {self.current_file}")
                return
            
            try:
                with open(self.current_file, "r", encoding="utf-8") as f:
                    content = f.read()
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
                self.status_bar.config(text=f"已重新打开: {self.current_file}")
                self.update_status()
                self.update_preview()
            except Exception as e:
                messagebox.showerror("错误", f"打开文件失败: {str(e)}")
        else:
            messagebox.showinfo("提示", "没有最近打开的文件")
    def bind_shortcuts(self):
       
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-l>', self.reopen_last_file)
if __name__ == "__main__":
    root = tk.Tk()    
   
    app = EnhancedMarkdownEditor(root)
    root.mainloop()