# Qnote - A Lightweight Markdown Editor

[中文](README.md)
[English](README_EN.md)

![Screenshot](p1.png) 

Qnote is a modern Markdown editor developed based on Python Tkinter. It supports real-time preview, syntax highlighting, and a variety of practical functions, making it suitable for daily note-taking and technical document writing.


## Features
Real-time Dual-pane Preview: Edit on the left and instantly see the rendered effect on the right.
Intelligent Syntax Highlighting: Automatically identify and highlight:
- Headings (#)
- Bold/Italic (** ** / * *)
- Code Blocks (```)
- Mathematical Formulas ($ $)
- Hyperlinks and Images

**Theme Switching:**

Support for light/dark modes.
Outline View: Automatically generate a document structure navigation.

**Version Control:**

Unlimited Undo/Redo (Ctrl+Z/Y)
Automatic Save Function (every 30 seconds)
Convenient Tools:
Insert commonly used elements with one click (headings/links/images, etc.)
Find and Replace function (supports global replacement)
Word count and cursor position display
Format Export: Complete HTML export (with support for mathematical formulas)
Installation and Usage
Environment Requirements
Python 3.6+
Dependent Libraries:
```bash
pip install markdown
```
## Launch Methods
### Method 1
```bash
git clone https://github.com/Reoame/Qnote.git
cd Qnote
python qnote.py
```
### Method 2

Download the executable program directly from the Release page.

List of Shortcut Keys
Function Shortcut Key
- **New File Ctrl + N**
- **Open File Ctrl + O**
- **Save File Ctrl + S**
- **Undo Operation Ctrl + Z**
- **Redo Operation Ctrl + Y**
- **Reopen File Ctrl + L**

Open File Ctrl + O
Save File Ctrl + S
Undo Operation Ctrl + Z
Redo Operation Ctrl + Y
Reopen File Ctrl + L
Theme Switching
You can switch between light and dark themes through the menu bar View → Switch Theme or the toolbar button:
Light Theme: Suitable for daytime use.
Dark Theme: Low blue light eye protection mode.
Export HTML
Click File → Export HTML
Select the save path.
Generate a complete HTML file with the following features:
Responsive layout
Code highlighting
Mathematical formula rendering (MathJax)
Beautiful 排版样式
Contribute
## You are welcome to participate in the project in the following ways:
Submit Issues to report problems.
Fork the repository and submit Pull Requests.
Improve the documentation or translations.
Contribution Guidelines
Technical Support
If you encounter any problems, please contact:
Author: Reoame

GitHub: Reoame

Email: reoame_github@outlook.com

Submit issues in the project repository.
## Future Plans
Add more language versions.
Open Source License
This project is licensed under the MIT License.
