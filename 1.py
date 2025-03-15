import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import markdown
import os
import re
import webbrowser
import shutil
from glob import glob
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class EnhancedMarkdownEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Qnote Pro")
        self.root.geometry("1400x900")
        self.current_file = None
        self.theme_mode = "light"
        self.modified = False
        self.setup_ui()
        self.create_menu()
        self.create_toolbar()
        self.create_statusbar()
        self.bind_shortcuts()
        self.set_theme("light")
        self.setup_highlight_tags()
        self.setup_preview_style()
        self.setup_autosave()

    def setup_ui(self):
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(expand=True, fill='both', padx=5, pady=5)

        # 左侧编辑器
        self.editor_frame = ttk.Frame(self.main_paned)
        self.text_area = scrolledtext.ScrolledText(
            self.editor_frame,
            wrap=tk.WORD,
            font=('Consolas', 12),
            undo=True,
            autoseparators=True,
            maxundo=-1
        )
        self.text_area.pack(expand=True, fill='both')
        self.main_paned.add(self.editor_frame, weight=2)

        # 右侧预览面板
        self.preview_frame = ttk.Frame(self.main_paned)
        self.preview_paned = ttk.PanedWindow(self.preview_frame, orient=tk.VERTICAL)
        
        # 大纲视图
        self.outline_tree = ttk.Treeview(self.preview_paned)
        self.preview_paned.add(self.outline_tree, weight=1)
        
        # 预览区域
        self.preview_area = scrolledtext.ScrolledText(
            self.preview_paned,
            wrap=tk.WORD,
            font=('Helvetica', 12),
            state='disabled'
        )
        self.preview_paned.add(self.preview_area, weight=3)
        self.preview_paned.pack(expand=True, fill='both')
        self.main_paned.add(self.preview_frame, weight=2)

        self.text_area.bind('<KeyRelease>', self.on_content_changed)

    # [其他方法保持与之前提供的EnhancedMarkdownEditor完全一致]
    # 此处为节省篇幅省略具体实现，实际需要完整保留

class KnowledgeGraphEditor(EnhancedMarkdownEditor):
    def __init__(self, root):
        super().__init__(root)
        self.custom_css = None
        self.notes_dir = os.path.expanduser("~/Qnotes")
        self.knowledge_graph = KnowledgeGraph()
        self.current_folder = None
        self.tree_context_menu = None
        self.setup_customizations()
        self.setup_wikilinks()
        self.setup_graph_view()
        self.setup_note_structure()

    def create_menu(self):
        super().create_menu()
        # 在文件菜单添加打开文件夹选项
        self.root.nametowidget(".menu.file").insert_command(
            4,  # 插入在"打开"和"保存"之间
            label="打开文件夹",
            command=self.open_folder,
            accelerator="Ctrl+Shift+O"
        )

    def setup_customizations(self):
        """扩展视图菜单"""
        self.view_menu.add_separator()
        
        # CSS操作菜单
        css_menu = tk.Menu(self.view_menu, tearoff=0)
        css_menu.add_command(label="加载CSS", command=self.load_custom_css)
        css_menu.add_command(label="重置CSS", command=self.reset_custom_css)
        self.view_menu.add_cascade(label="主题样式", menu=css_menu)
        
        # 知识图谱子菜单
        kg_menu = tk.Menu(self.view_menu, tearoff=0)
        kg_menu.add_command(label="显示图谱", command=self.toggle_graph)
        kg_menu.add_command(label="刷新图谱", command=self.update_graph)
        self.view_menu.add_cascade(label="知识图谱", menu=kg_menu)

    def setup_wikilinks(self):
        self.text_area.tag_configure("wikilink", foreground="#9b59b6", underline=True)
        self.text_area.tag_bind("wikilink", "<Button-1>", self.on_wikilink_click)

    def setup_graph_view(self):
        self.graph_frame = ttk.Frame(self.preview_paned)
        self.figure = plt.Figure(figsize=(5,4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.preview_paned.add(self.graph_frame, weight=2)
        self.update_graph()

    def setup_note_structure(self):
        self.tree_pane = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL)
        self.tree_container = ttk.Frame(self.tree_pane)
        
        # 创建带滚动条的树状视图
        self.note_tree = ttk.Treeview(self.tree_container, show='tree', selectmode='browse')
        self.tree_scroll = ttk.Scrollbar(self.tree_container, orient="vertical", command=self.note_tree.yview)
        self.note_tree.configure(yscrollcommand=self.tree_scroll.set)
        
        # 布局
        self.note_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_container.pack(fill=tk.BOTH, expand=True)
        
        self.tree_pane.add(self.tree_container)
        self.main_paned.insert(0, self.tree_pane)
        
        # 绑定事件
        self.note_tree.bind("<Double-1>", self.on_tree_double_click)
        self.note_tree.bind("<Button-3>", self.show_tree_context_menu)
        self.root.bind("<Control-Shift-O>", lambda e: self.open_folder())

    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.current_folder = folder_path
            self.load_note_structure()
            self.status_bar.config(text=f"已打开文件夹：{folder_path}")

    def load_note_structure(self, parent='', path=None):
        if not path:
            path = self.current_folder
            self.note_tree.delete(*self.note_tree.get_children())
            
        try:
            for item in sorted(os.listdir(path), key=lambda x: (not os.path.isdir(os.path.join(path, x)), x)):
                item_path = os.path.join(path, item)
                is_dir = os.path.isdir(item_path)
                
                node = self.note_tree.insert(
                    parent, 'end', 
                    text=item,
                    values=[item_path],
                    tags=('directory' if is_dir else 'file')
                )
                
                if is_dir:
                    self.load_note_structure(node, item_path)
        except PermissionError:
            messagebox.showerror("权限错误", "无法访问该目录")
        except Exception as e:
            messagebox.showerror("错误", f"加载目录失败：{str(e)}")

    def on_tree_double_click(self, event):
        item = self.note_tree.selection()[0]
        path = self.note_tree.item(item, "values")[0]
        
        if os.path.isfile(path) and path.endswith('.md'):
            self.open_file(path)

    def show_tree_context_menu(self, event):
        item = self.note_tree.identify_row(event.y)
        if not item: return
        
        # 创建右键菜单
        self.tree_context_menu = tk.Menu(self.root, tearoff=0)
        path = self.note_tree.item(item, "values")[0]
        is_dir = os.path.isdir(path)
        
        # 通用操作
        self.tree_context_menu.add_command(
            label="重命名",
            command=lambda: self.rename_item(item)
        )
        self.tree_context_menu.add_command(
            label="删除",
            command=lambda: self.delete_item(item)
        )
        
        # 文件相关操作
        if not is_dir:
            self.tree_context_menu.add_command(
                label="打开",
                command=lambda: self.open_file(path)
            )
            self.tree_context_menu.add_separator()
            self.tree_context_menu.add_command(
                label="复制路径",
                command=lambda: self.root.clipboard_clear() or self.root.clipboard_append(path)
            )
        # 目录相关操作
        else:
            self.tree_context_menu.add_command(
                label="新建文件",
                command=lambda: self.create_new_file(item)
            )
            self.tree_context_menu.add_command(
                label="新建文件夹",
                command=lambda: self.create_new_folder(item)
            )
            self.tree_context_menu.add_separator()
            self.tree_context_menu.add_command(
                label="在资源管理器中打开",
                command=lambda: os.startfile(path)
            )
            
        self.tree_context_menu.tk_popup(event.x_root, event.y_root)

    def rename_item(self, item):
        old_path = self.note_tree.item(item, "values")[0]
        new_name = simpledialog.askstring("重命名", "输入新名称：", initialvalue=os.path.basename(old_path))
        
        if new_name and new_name != os.path.basename(old_path):
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            try:
                os.rename(old_path, new_path)
                self.load_note_structure()
            except Exception as e:
                messagebox.showerror("错误", f"重命名失败：{str(e)}")

    def delete_item(self, item):
        path = self.note_tree.item(item, "values")[0]
        confirm = messagebox.askyesno("确认删除", f"确定要永久删除 {os.path.basename(path)} 吗？")
        
        if confirm:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)
                self.load_note_structure()
            except Exception as e:
                messagebox.showerror("错误", f"删除失败：{str(e)}")

    def create_new_file(self, parent_item):
        parent_path = self.note_tree.item(parent_item, "values")[0]
        file_name = simpledialog.askstring("新建文件", "输入文件名（包含.md扩展名）：")
        
        if file_name:
            if not file_name.endswith('.md'):
                file_name += '.md'
                
            file_path = os.path.join(parent_path, file_name)
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {os.path.splitext(file_name)[0]}\n\n")
                self.load_note_structure()
            except Exception as e:
                messagebox.showerror("错误", f"创建文件失败：{str(e)}")

    def create_new_folder(self, parent_item):
        parent_path = self.note_tree.item(parent_item, "values")[0]
        folder_name = simpledialog.askstring("新建文件夹", "输入文件夹名称：")
        
        if folder_name:
            folder_path = os.path.join(parent_path, folder_name)
            try:
                os.makedirs(folder_path, exist_ok=True)
                self.load_note_structure()
            except Exception as e:
                messagebox.showerror("错误", f"创建文件夹失败：{str(e)}")

    def load_custom_css(self):
        css_file = filedialog.askopenfilename(filetypes=[("CSS Files", "*.css")])
        if css_file:
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    self.custom_css = f.read()
                self.update_preview()
                messagebox.showinfo("成功", "自定义CSS已加载")
            except UnicodeDecodeError:
                messagebox.showerror("编码错误", "无法读取CSS文件，请确保文件使用UTF-8编码")
            except Exception as e:
                messagebox.showerror("加载失败", f"发生未知错误：{str(e)}")

    def reset_custom_css(self):
        self.custom_css = None
        self.update_preview()
        messagebox.showinfo("提示", "CSS样式已重置为默认")

    def update_preview(self):
        self.preview_area.config(state='normal')
        self.preview_area.delete(1.0, tk.END)
        if self.custom_css:
            self.preview_area.insert(tk.END, f'<style>{self.custom_css}</style>\n', 'css')
        super().update_preview()

    def on_wikilink_click(self, event):
        index = self.text_area.index(f"@{event.x},{event.y}")
        line_start = self.text_area.index(f"{index} linestart")
        line_end = self.text_area.index(f"{index} lineend")
        line_text = self.text_area.get(line_start, line_end)
        
        if match := re.search(r'\[\[(.*?)\]\]', line_text):
            link_text = match.group(1)
            self.open_wikilink(link_text)

    def open_wikilink(self, link):
        target_file = os.path.join(self.notes_dir, f"{link}.md")
        if os.path.exists(target_file):
            self.open_file(target_file)
        else:
            if messagebox.askyesno("创建笔记", f"创建新笔记 '{link}'?"):
                os.makedirs(self.notes_dir, exist_ok=True)
                with open(target_file, 'w') as f:
                    f.write(f"# {link}\n\n")
                self.load_note_structure()
                self.open_file(target_file)

    def update_graph(self):
        self.knowledge_graph.update_graph(self.notes_dir)
        self.figure.clf()
        ax = self.figure.add_subplot(111)
        pos = nx.spring_layout(self.knowledge_graph.graph)
        nx.draw(self.knowledge_graph.graph, pos, ax=ax, with_labels=True, 
                node_color='skyblue', node_size=2000, arrowsize=20)
        self.canvas.draw()
        self.root.after(5000, self.update_graph)

    def toggle_graph(self):
        if self.graph_frame.winfo_ismapped():
            self.preview_paned.forget(self.graph_frame)
        else:
            self.preview_paned.add(self.graph_frame)

    def export_html(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML文件", "*.html")]
        )
        if file_path:
            content = self.text_area.get("1.0", "end-1c")
            html = markdown.markdown(content, extensions=['tables', 'fenced_code'])
            full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{os.path.splitext(os.path.basename(file_path))[0]}</title>
    <style>{self.get_preview_styles()}</style>
    {f'<style>{self.custom_css}</style>' if self.custom_css else ''}
</head>
<body>
    <article>{html}</article>
</body>
</html>"""
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(full_html)
                messagebox.showinfo("导出成功", f"HTML文件已保存到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("导出失败", f"保存文件时出错:\n{str(e)}")

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def update_graph(self, notes_dir):
        self.graph.clear()
        md_files = glob(os.path.join(notes_dir, '**/*.md'), recursive=True)
        
        for file in md_files:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                links = re.findall(r'\[\[(.*?)\]\]', content)
                source = os.path.splitext(os.path.basename(file))[0]
                self.graph.add_node(source)
                for target in links:
                    self.graph.add_edge(source, target)

if __name__ == "__main__":
    root = tk.Tk()
    app = KnowledgeGraphEditor(root)
    root.mainloop()