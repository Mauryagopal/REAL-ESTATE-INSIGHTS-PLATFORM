import os
import re

# 🧠 Folders to ignore
IGNORE_FOLDERS = {'.venv', '.git', '__pycache__', '.ipynb_checkpoints', '.mypy_cache'}

def tree_to_md(path, prefix=''):
    """Recursively build a Markdown-style directory tree, skipping ignored folders."""
    items = sorted(os.listdir(path))
    md = ''
    for i, item in enumerate(items):
        full_path = os.path.join(path, item)
        if item in IGNORE_FOLDERS:
            continue
        connector = '└── ' if i == len(items) - 1 else '├── '
        md += f"{prefix}{connector}{item}\n"
        if os.path.isdir(full_path):
            md += tree_to_md(full_path, prefix + ('    ' if i == len(items) - 1 else '│   '))
    return md


# --- Generate tree ---
project_path = '.'  
tree_md = tree_to_md(project_path)

# --- Read current README.md ---
readme_path = 'README.md'
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
else:
    content = '# Project Documentation\n\n'

# --- Replace or insert the folder structure section ---
section_pattern = re.compile(r'## 📁 Project Folder Structure[\s\S]*?(?=\n## |\Z)', re.MULTILINE)
new_section = f"## 📁 Project Folder Structure\n\n```\n{tree_md}```\n"

if section_pattern.search(content):
    content = section_pattern.sub(new_section, content)
else:
    content += '\n' + new_section

# --- Write back ---
with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Clean folder structure added/updated in README.md (ignored .venv and cache folders)")
