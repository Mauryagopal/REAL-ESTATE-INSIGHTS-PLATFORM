import os
import re

def tree_to_md(path, prefix=''):
    """Recursively build a Markdown-style directory tree."""
    items = sorted(os.listdir(path))
    md = ''
    for i, item in enumerate(items):
        full_path = os.path.join(path, item)
        connector = '└── ' if i == len(items)-1 else '├── '
        md += f"{prefix}{connector}{item}\n"
        if os.path.isdir(full_path):
            md += tree_to_md(full_path, prefix + ('    ' if i == len(items)-1 else '│   '))
    return md


# --- Step 1: Generate tree structure ---
project_path = '.'  # Root folder
tree_md = tree_to_md(project_path)

# --- Step 2: Read current README.md (if exists) ---
readme_path = 'README.md'
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
else:
    content = '# Project Documentation\n\n'

# --- Step 3: Replace or insert the "Project Folder Structure" section ---
section_pattern = re.compile(r'## 📁 Project Folder Structure[\s\S]*?(?=\n## |\Z)', re.MULTILINE)
new_section = f"## 📁 Project Folder Structure\n\n```\n{tree_md}```\n"

if section_pattern.search(content):
    # Replace existing section
    content = section_pattern.sub(new_section, content)
else:
    # Append new section at the end
    content += '\n' + new_section

# --- Step 4: Write back to README.md ---
with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Folder structure added/updated successfully in README.md!")
