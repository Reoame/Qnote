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
        self.setup_preview_style()
        #self.markdown_help()
        self.setup_autosave()

    def setup_ui(self):
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(expand=True, fill='both', padx=5, pady=5)

        # Left editor
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
        main_paned.add(self.editor_frame, weight=1)

        # Right preview panel
        self.preview_frame = ttk.Frame(main_paned)
        self.preview_paned = ttk.PanedWindow(self.preview_frame, orient=tk.VERTICAL)
        
        # Outline view
        self.outline_tree = ttk.Treeview(self.preview_paned)
        self.preview_paned.add(self.outline_tree, weight=1)
        
        # Preview area
        self.preview_area = scrolledtext.ScrolledText(
            self.preview_paned,
            wrap=tk.WORD,
            font=('Helvetica', 12),
            state='disabled'
        )
        self.preview_paned.add(self.preview_area, weight=3)
        self.preview_paned.pack(expand=True, fill='both')
        main_paned.add(self.preview_frame, weight=1)

        self.text_area.bind('<KeyRelease>', self.on_content_changed)

    def setup_preview_style(self):
        """Configure preview area text style"""
        self.preview_area.tag_configure("h1", font=('Helvetica', 20, 'bold'), foreground="#2c3e50")
        self.preview_area.tag_configure("h2", font=('Helvetica', 18, 'bold'), foreground="#2c3e50")
        self.preview_area.tag_configure("h3", font=('Helvetica', 16, 'bold'), foreground="#2c3e50")
        self.preview_area.tag_configure("bold", font=('Helvetica', 12, 'bold'))
        self.preview_area.tag_configure("italic", font=('Helvetica', 12, 'italic'))
        self.preview_area.tag_configure("code", font=('Consolas', 12), background="#f0f0f0")
        self.preview_area.tag_configure("quote", foreground="#666666", lmargin1=20, spacing3=5)
        self.preview_area.tag_configure("link", foreground="#3498db", underline=1)
        self.preview_area.tag_configure("list", lmargin1=20, spacing3=5)
    
    def update_preview(self):
        """Convert Markdown to formatted preview"""
        self.preview_area.config(state='normal')
        self.preview_area.delete(1.0, tk.END)
        
        content = self.text_area.get(1.0, tk.END)
        lines = content.split('\n')
        
        for line in lines:
            if re.match(r'^#+ ', line):
                self.process_header(line)
            elif re.match(r'^[\-\*\+] ', line):
                self.process_list(line)
            elif line.startswith('> '):
                self.process_quote(line)
            elif line.startswith('    ') or line.startswith('\t'):
                self.process_code(line)
            else:
                self.process_inline_styles(line)
        
        self.preview_area.config(state='disabled')

    def process_header(self, line):
        level = len(re.match(r'^(#+)', line).group(1))
        text = re.sub(r'^#+ ', '', line)
        tag = f"h{min(level, 3)}"
        self.preview_area.insert(tk.END, text + '\n', tag)

    def process_list(self, line):
        self.preview_area.insert(tk.END, '• ' + line[2:] + '\n', ("list",))

    def process_quote(self, line):
        self.preview_area.insert(tk.END, line[2:] + '\n', ("quote",))

    def process_code(self, line):
        self.preview_area.insert(tk.END, line.strip() + '\n', ("code",))

    def process_inline_styles(self, line):
        patterns = [
            (r'\*\*(.*?)\*\*', "bold"),
            (r'\*(.*?)\*', "italic"),
            (r'`(.*?)`', "code"),
            (r'\[(.*?)\]\((.*?)\)', "link")
        ]
        
        temp_line = line
        for pattern, tag in patterns:
            parts = re.split(pattern, temp_line)
            temp_line = ""
            for i in range(len(parts)):
                if i % 2 == 1:
                    self.preview_area.insert(tk.END, parts[i], tag)
                else:
                    self.preview_area.insert(tk.END, parts[i])
            temp_line = self.preview_area.get("end-1c linestart", "end-1c")
            self.preview_area.delete("end-1c linestart", "end-1c")
        
        self.preview_area.insert(tk.END, '\n')

    # The following are the complete implementations of the original features
    def helpus(self):
        webbrowser.open("https://github.com/Reoame/Qnote/issues</url> ")

    def open_web_about(self):
        webbrowser.open("https://reoame.github.io/Mypage/about.html</url> ")

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Export HTML", command=self.export_html)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        file_menu.add_command(label="Give us feedback", command=self.helpus)
        file_menu.add_command(label="About", command=self.open_web_about)
        menu_bar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find and Replace", command=self.show_search_dialog)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        view_menu.add_checkbutton(label="Syntax Highlighting", variable=tk.BooleanVar(value=True))
        menu_bar.add_cascade(label="View", menu=view_menu)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu_bar)
        help_menu.add_command(label="Markdown Syntax Tutorial", command=self.markdown_help)
        help_menu.add_command(label="GitHub Repository", command=self.github_help)
    def markdown_help(self):
        webbrowser.open("https://markdown.com")
    def github_help(self):
        webbrowser.open("https://github.com/Reoame/Qnote/issues ")
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
            ("C", lambda: self.wrap_selection("``")),
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
            text="Ready | Line: 1 | Column: 1 | Word Count: 0",
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
        patterns = [
            (r'^(#{1,6})\s+(.+)$', "header", re.M),
            (r'\*\*(.*?)\*\*', "bold"),
            (r'\*(.*?)\*', "italic"),
            (r'`(.*?)`', "code"),
            (r'\[.*?\]\(.*?\)', "link"),
            (r'\$(.*?)\$', "math")
        ]

        for pattern, tag, *flags in patterns:
            flags = flags[0] if flags else 0
            for match in re.finditer(pattern, content, flags):
                start = f"1.0 + {match.start()}c"
                end = f"1.0 + {match.end()}c"
                self.text_area.tag_add(tag, start, end)

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
        self.preview_area.config(bg=t['text_bg'], fg=t['fg'])
        self.status_bar.config(background=t['status_bg'], foreground=t['fg'])
        self.root.config(bg=t['bg'])
        self.theme_mode = theme

    def new_file(self):
        self.text_area.delete("1.0", "end")
        self.current_file = None
        self.update_status()

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
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
                messagebox.showerror("Error", f"Cannot open file: {str(e)}")

    def save_file(self):
        if self.current_file:
            try:
                content = self.text_area.get("1.0", "end-1c")
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(content)
                self.status_bar.config(text="File saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Save failed: {str(e)}")
        else:
            self.save_as_file()

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            self.save_file()

    def export_html(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html")]
        )
        if not file_path:
            return
    
        content = self.text_area.get("1.0", "end-1c")
        html = markdown.markdown(content, extensions=['tables', 'fenced_code'])
    
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{os.path.splitext(os.path.basename(file_path))[0]}</title>
    <style>{self.get_preview_styles()}</style>
</head>
<body>
    <article>{html}</article>
</body>
</html>"""
    
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(full_html)
            messagebox.showinfo("Export Successful", f"HTML file has been saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred while saving the file:\n{str(e)}")

    def get_preview_styles(self):
        return """
        /* Basic settings */
            /* Basic settings */
:root {
    --primary-color: #2c3e50;
    --accent-color: #3498db;
    --text-color: #34495e;
    --background-color: #f8f9fa;
    --code-bg: #f4f4f4;
    --border-radius: 8px;
    --shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Main styles */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
                 Oxygen, Ubuntu, Cantarell, 'Open Sans', sans-serif;
    line-height: 1.8;
    color: var(--text-color);
    background-color: var(--background-color);
    max-width: 800px;
    margin: 2rem auto;
    padding: 2rem;
    letter-spacing: 0.02em;
}

/* Header styles */
h1, h2, h3 {
    color: var(--primary-color);
    position: relative;
    padding-bottom: 0.5rem;
    margin: 2rem 0 1.5rem;
}

h1::after, h2::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    width: 3rem;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-color), transparent);
}

/* Code block styles */
pre {
    background: linear-gradient(145deg, #ffffff, var(--code-bg));
    padding: 1.5rem;
    border-radius: var(--border-radius);
    overflow-x: auto;
    box-shadow: var(--shadow);
    margin: 1.5rem 0;
    border: 1px solid rgba(0, 0, 0, 0.05);
}

code {
    font-family: 'Fira Code', 'Consolas', monospace;
    background: rgba(var(--accent-color), 0.1);
    color: #e74c3c;
    padding: 0.2em 0.4em;
    border-radius: 4px;
    transition: background 0.2s;
}

pre code {
    background: transparent;
    color: inherit;
    padding: 0;
}

/* Table styles */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 2rem 0;
    box-shadow: var(--shadow);
    border-radius: var(--border-radius);
    overflow: hidden;
}

th {
    background-color: var(--accent-color);
    color: white;
    font-weight: 600;
    padding: 1rem;
    text-align: left;
}

td {
    padding: 1rem;
    background: white;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

tr:hover td {
    background-color: rgba(var(--accent-color), 0.03);
}

/* Blockquote styles */
blockquote {
    border-left: 4px solid var(--accent-color);
    padding: 10px;
    background: rgba(var(--accent-color), 0.03);
    border-radius: 0 var(--border-radius) var(--border-radius) 0;
    font-style: italic;
    color: var(--primary-color);
}

/* Link styles */
a {
    color: var(--accent-color);
    text-decoration: none;
    position: relative;
    transition: color 0.3s ease;
}

a::after {
    content: "";
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 0;
    height: 1px;
    background: currentColor;
    transition: width 0.3s ease;
}

a:hover {
    color: #2980b9;
}

a:hover::after {
    width: 100%;
}

/* Math formula styles */
.math {
    color: #c0392b;
    font-family: "TeX", "Latin Modern Math", serif;
}

/* Responsive design */
@media (max-width: 768px) {
    body {
        padding: 1rem;
        margin: 1rem;
    }
    
    pre {
        border-radius: 0;
        margin-left: -1rem;
        margin-right: -1rem;
    }
}

/* Scrollbar beautification */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.05);
}

::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--accent-color);
}
        """

    def toggle_theme(self):
        self.set_theme("dark" if self.theme_mode == "light" else "light")

    def update_status(self):
        text = self.text_area.get("1.0", "end-1c")
        char_count = len(text)
        words = len(text.split())
        lines = text.count('\n') + 1
        current_line, current_col = self.text_area.index(tk.INSERT).split('.')
        status_text = f"Status: {'Saved' if self.current_file else 'Unsaved'} | Line: {current_line} | Column: {current_col} | Character Count: {char_count} | Word Count: {words}"
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
        self.text_area.insert(tk.INSERT, "[Display text](http://)")
        self.text_area.mark_set(tk.INSERT, "insert-9c")
    def insert_image(self):
        self.text_area.insert(tk.INSERT, "![Description](Image URL)")
        self.text_area.mark_set(tk.INSERT, "insert-9c")

    def insert_math(self):
        self.text_area.insert(tk.INSERT, "$Formula$")
        self.text_area.mark_set(tk.INSERT, "insert-1c")

    def show_search_dialog(self):
        search_win = tk.Toplevel(self.root)
        search_win.resizable(False, False)
        search_win.title("Find and Replace")
        
        ttk.Label(search_win, text="Find:").grid(row=0, column=0, padx=5, pady=5)
        self.search_entry = ttk.Entry(search_win, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(search_win, text="Replace with:").grid(row=1, column=0, padx=5, pady=5)
        self.replace_entry = ttk.Entry(search_win, width=30)
        self.replace_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(search_win, text="Find Next", command=self.find_next).grid(row=0, column=2, padx=5)
        ttk.Button(search_win, text="Replace", command=self.replace_text).grid(row=1, column=2, padx=5)
        ttk.Button(search_win, text="Replace All", command=self.replace_all).grid(row=2, column=2, padx=5)

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

    def bind_shortcuts(self):
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedMarkdownEditor(root)
    root.mainloop()