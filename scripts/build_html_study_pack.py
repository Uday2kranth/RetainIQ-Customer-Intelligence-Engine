#!/usr/bin/env python3
"""
RetainIQ: Study Pack HTML5 Generator
Converts all Markdown guides and Python skeletons into responsive,
self-contained, standalone HTML5 documents with embedded base64 images,
dynamic Light/Dark mode toggling, and persistent theme storage.
"""

import os
import re
import base64
import mimetypes
from pathlib import Path
import markdown

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXTERNAL_STUDY_PACK_DIR = Path(r"D:\important_cmd_history\study_pack")
STUDY_PACK_DIR = EXTERNAL_STUDY_PACK_DIR if EXTERNAL_STUDY_PACK_DIR.exists() else PROJECT_ROOT / "study_pack"

CSS_STYLES = """
:root {
  --bg-primary: #0b0f19;
  --bg-secondary: #131b2e;
  --bg-card: #182238;
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --accent-cyan: #38bdf8;
  --accent-blue: #60a5fa;
  --accent-green: #4ade80;
  --accent-red: #f87171;
  --accent-amber: #fbbf24;
  --border-color: #27354f;
  --code-bg: #0d1322;
  --code-text: #e2e8f0;
  --table-stripe: rgba(255, 255, 255, 0.02);
  --table-hover: rgba(56, 189, 248, 0.05);
  --quote-bg: rgba(30, 41, 59, 0.7);
  --shadow-color: rgba(0, 0, 0, 0.4);
}

[data-theme="light"] {
  --bg-primary: #f8fafc;
  --bg-secondary: #f1f5f9;
  --bg-card: #ffffff;
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;
  --accent-cyan: #0284c7;
  --accent-blue: #2563eb;
  --accent-green: #16a34a;
  --accent-red: #dc2626;
  --accent-amber: #d97706;
  --border-color: #e2e8f0;
  --code-bg: #f1f5f9;
  --code-text: #1e293b;
  --table-stripe: rgba(0, 0, 0, 0.02);
  --table-hover: rgba(2, 132, 199, 0.05);
  --quote-bg: rgba(241, 245, 249, 0.85);
  --shadow-color: rgba(0, 0, 0, 0.08);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.65;
  font-size: 16px;
  padding: 1rem;
  max-width: 900px;
  margin: 0 auto;
}

@media (min-width: 768px) {
  body {
    padding: 2.5rem 1.5rem;
    font-size: 17px;
  }
}

/* Header & Breadcrumbs */
header.nav-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.25rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 0.75rem;
  box-shadow: 0 4px 15px var(--shadow-color);
}

header.nav-header a {
  color: var(--accent-cyan);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

header.nav-header a:hover {
  text-decoration: underline;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

/* Theme Toggle Button */
.theme-toggle-btn {
  background: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 0.35rem 0.8rem;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.theme-toggle-btn:hover {
  border-color: var(--accent-cyan);
  color: var(--accent-cyan);
}

.badge {
  background: rgba(56, 189, 248, 0.15);
  color: var(--accent-cyan);
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  border: 1px solid rgba(56, 189, 248, 0.3);
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
  color: var(--text-primary);
  font-weight: 700;
  line-height: 1.3;
  margin-top: 1.8rem;
  margin-bottom: 0.8rem;
}

h1 {
  font-size: 1.9rem;
  color: var(--accent-cyan);
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 0.6rem;
  margin-top: 0;
}

h2 {
  font-size: 1.45rem;
  color: var(--accent-blue);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.4rem;
}

h3 {
  font-size: 1.2rem;
  color: var(--text-primary);
}

p {
  margin-bottom: 1.1rem;
  color: var(--text-secondary);
}

/* Blockquotes (Voice Mode / Alert Callouts) */
blockquote {
  background: var(--quote-bg);
  border-left: 4px solid var(--accent-cyan);
  padding: 1rem 1.25rem;
  border-radius: 0 10px 10px 0;
  margin: 1.25rem 0;
  color: var(--text-primary);
  box-shadow: 0 4px 15px var(--shadow-color);
}

blockquote p:last-child {
  margin-bottom: 0;
}

blockquote strong {
  color: var(--accent-cyan);
}

/* Lists */
ul, ol {
  margin-left: 1.5rem;
  margin-bottom: 1.2rem;
  color: var(--text-secondary);
}

li {
  margin-bottom: 0.4rem;
}

/* Tables */
.table-container {
  overflow-x: auto;
  margin: 1.5rem 0;
  border-radius: 10px;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  -webkit-overflow-scrolling: touch;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.95rem;
}

th, td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color);
}

th {
  background-color: var(--bg-secondary);
  color: var(--accent-cyan);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.05em;
}

tr:nth-child(even) td {
  background-color: var(--table-stripe);
}

tr:hover td {
  background-color: var(--table-hover);
}

/* Code & Preformatted */
code {
  font-family: "JetBrains Mono", Consolas, Monaco, "Courier New", monospace;
  background: var(--code-bg);
  color: var(--accent-cyan);
  padding: 0.15rem 0.4rem;
  border-radius: 5px;
  font-size: 0.88em;
  border: 1px solid var(--border-color);
}

pre {
  background: var(--code-bg);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 1.25rem;
  overflow-x: auto;
  margin: 1.25rem 0;
  box-shadow: 0 4px 15px var(--shadow-color);
}

pre code {
  background: transparent;
  padding: 0;
  border: none;
  font-size: 0.9rem;
  color: var(--code-text);
  line-height: 1.5;
}

/* Images */
img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 1.5rem auto;
  border-radius: 10px;
  border: 1px solid var(--border-color);
  box-shadow: 0 8px 30px var(--shadow-color);
}

/* Horizontal Rule */
hr {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: 2rem 0;
}

/* Footer & Navigation */
footer.nav-footer {
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.nav-btn {
  display: inline-block;
  padding: 0.6rem 1.2rem;
  background: var(--bg-card);
  color: var(--accent-cyan);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.nav-btn:hover {
  background: rgba(56, 189, 248, 0.15);
  border-color: var(--accent-cyan);
}

/* Skeleton Code Card */
.code-skeleton-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.25rem;
  margin: 2rem 0;
}

.code-skeleton-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  color: var(--accent-green);
  font-weight: 600;
}
"""

THEME_SCRIPT = """
  <script>
    (function() {
      const savedTheme = localStorage.getItem('retainiq_theme') || 'dark';
      document.documentElement.setAttribute('data-theme', savedTheme);
    })();

    function updateThemeUI(theme) {
      const icon = document.getElementById('themeIcon');
      const text = document.getElementById('themeText');
      if (icon) icon.textContent = theme === 'light' ? '☀️' : '🌙';
      if (text) text.textContent = theme === 'light' ? 'Light' : 'Dark';
    }

    function toggleTheme() {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const target = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', target);
      localStorage.setItem('retainiq_theme', target);
      updateThemeUI(target);
    }

    window.addEventListener('DOMContentLoaded', () => {
      const activeTheme = document.documentElement.getAttribute('data-theme') || 'dark';
      updateThemeUI(activeTheme);
    });
  </script>
"""

def image_to_base64(img_path: Path) -> str:
    if not img_path.exists():
        return ""
    mime_type, _ = mimetypes.guess_type(str(img_path))
    if not mime_type:
        mime_type = "image/png"
    with open(img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"

def inline_images_in_markdown(md_content: str, base_dir: Path) -> str:
    def replace_img(match):
        alt = match.group(1)
        img_rel = match.group(2)
        if img_rel.startswith("http://") or img_rel.startswith("https://") or img_rel.startswith("data:"):
            return match.group(0)
        clean_rel = img_rel.replace("./", "").replace("/", os.sep)
        local_path = (base_dir / clean_rel).resolve()
        if local_path.exists():
            data_uri = image_to_base64(local_path)
            return f"![{alt}]({data_uri})"
        return match.group(0)
    return re.sub(r"!\[(.*?)\]\((.*?)\)", replace_img, md_content)

def wrap_tables_in_div(html_content: str) -> str:
    return re.sub(r"(<table>[\s\S]*?<\/table>)", r'<div class="table-container">\1</div>', html_content)

def convert_md_to_html(md_path: Path, output_path: Path, prev_link=None, next_link=None, skeleton_path: Path = None):
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    md_text = inline_images_in_markdown(md_text, md_path.parent)
    body_html = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'nl2br'])
    body_html = wrap_tables_in_div(body_html)

    skeleton_html = ""
    if skeleton_path and skeleton_path.exists():
        with open(skeleton_path, "r", encoding="utf-8") as sf:
            code_text = sf.read()
        skeleton_html = f"""
        <div class="code-skeleton-card">
          <div class="code-skeleton-header">
            <span>💻 25-Line Code Skeleton ({skeleton_path.name})</span>
            <span class="badge">Pure Python</span>
          </div>
          <pre><code>{code_text}</code></pre>
        </div>
        """

    prev_btn = f'<a href="{prev_link}" class="nav-btn">← Previous Module</a>' if prev_link else '<span></span>'
    next_btn = f'<a href="{next_link}" class="nav-btn">Next Module →</a>' if next_link else '<span></span>'

    first_h1 = re.search(r"<h1.*?>(.*?)<\/h1>", body_html)
    page_title = first_h1.group(1) if first_h1 else md_path.stem

    full_html = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RetainIQ Defense: {page_title}</title>
  {THEME_SCRIPT}
  <style>
    {CSS_STYLES}
  </style>
</head>
<body>
  <header class="nav-header">
    <a href="../index.html">🏠 RetainIQ Defense Hub</a>
    <div class="header-right">
      <button class="theme-toggle-btn" onclick="toggleTheme()" aria-label="Toggle Light/Dark Theme">
        <span id="themeIcon">🌙</span> <span id="themeText">Dark</span>
      </button>
      <span class="badge">Interview Ready</span>
    </div>
  </header>

  <main>
    {body_html}
    {skeleton_html}
  </main>

  <footer class="nav-footer">
    {prev_btn}
    <a href="../index.html" class="nav-btn">🏠 Index</a>
    {next_btn}
  </footer>
</body>
</html>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"  [+] Generated: {output_path.name}")

def build_all():
    print("[*] Starting RetainIQ Study Pack HTML Generation with Light/Dark Mode...")
    
    modules = [
        {
            "stage": "STAGE 0",
            "icon": "⚡",
            "title": "Setup & Project Launch",
            "md_path": STUDY_PACK_DIR / "00_SETUP_&_LAUNCH" / "HOW_TO_RUN_PROJECT.md",
            "html_path": STUDY_PACK_DIR / "00_SETUP_&_LAUNCH" / "HOW_TO_RUN_PROJECT.html",
            "html_rel": "00_SETUP_&_LAUNCH/HOW_TO_RUN_PROJECT.html",
            "has_py": False
        },
        {
            "stage": "CHEAT SHEET",
            "icon": "🚀",
            "title": "Quick-Run & Defense Cheat Sheet",
            "md_path": STUDY_PACK_DIR / "00_QUICK_RUN_&_DEFENSE_CHEAT_SHEET.md",
            "html_path": STUDY_PACK_DIR / "00_QUICK_RUN_&_DEFENSE_CHEAT_SHEET.html",
            "html_rel": "00_QUICK_RUN_&_DEFENSE_CHEAT_SHEET.html",
            "has_py": False
        },
        {
            "stage": "STAGE 1",
            "icon": "🗄️",
            "title": "SQL Database & Ingestion",
            "md_path": STUDY_PACK_DIR / "01_SQL_DATABASE_&_INGESTION" / "EXPLAINER.md",
            "html_path": STUDY_PACK_DIR / "01_SQL_DATABASE_&_INGESTION" / "EXPLAINER.html",
            "html_rel": "01_SQL_DATABASE_&_INGESTION/EXPLAINER.html",
            "skeleton": STUDY_PACK_DIR / "01_SQL_DATABASE_&_INGESTION" / "skeleton_ingest.py",
            "has_py": True
        },
        {
            "stage": "STAGE 2",
            "icon": "📈",
            "title": "RFM Feature Engineering",
            "md_path": STUDY_PACK_DIR / "02_RFM_FEATURE_ENGINEERING" / "EXPLAINER.md",
            "html_path": STUDY_PACK_DIR / "02_RFM_FEATURE_ENGINEERING" / "EXPLAINER.html",
            "html_rel": "02_RFM_FEATURE_ENGINEERING/EXPLAINER.html",
            "skeleton": STUDY_PACK_DIR / "02_RFM_FEATURE_ENGINEERING" / "skeleton_rfm.py",
            "has_py": True
        },
        {
            "stage": "STAGE 3",
            "icon": "🌲",
            "title": "Random Forest ML Model",
            "md_path": STUDY_PACK_DIR / "03_MACHINE_LEARNING_MODEL" / "EXPLAINER.md",
            "html_path": STUDY_PACK_DIR / "03_MACHINE_LEARNING_MODEL" / "EXPLAINER.html",
            "html_rel": "03_MACHINE_LEARNING_MODEL/EXPLAINER.html",
            "skeleton": STUDY_PACK_DIR / "03_MACHINE_LEARNING_MODEL" / "skeleton_model.py",
            "has_py": True
        },
        {
            "stage": "STAGE 4",
            "icon": "📬",
            "title": "Gmail OAuth 2.0 Alerts",
            "md_path": STUDY_PACK_DIR / "04_GMAIL_OAUTH_ALERTS" / "EXPLAINER.md",
            "html_path": STUDY_PACK_DIR / "04_GMAIL_OAUTH_ALERTS" / "EXPLAINER.html",
            "html_rel": "04_GMAIL_OAUTH_ALERTS/EXPLAINER.html",
            "skeleton": STUDY_PACK_DIR / "04_GMAIL_OAUTH_ALERTS" / "skeleton_alert.py",
            "has_py": True
        },
        {
            "stage": "STAGE 5",
            "icon": "🌪️",
            "title": "Apache Airflow Orchestration",
            "md_path": STUDY_PACK_DIR / "05_APACHE_AIRFLOW" / "EXPLAINER.md",
            "html_path": STUDY_PACK_DIR / "05_APACHE_AIRFLOW" / "EXPLAINER.html",
            "html_rel": "05_APACHE_AIRFLOW/EXPLAINER.html",
            "skeleton": STUDY_PACK_DIR / "05_APACHE_AIRFLOW" / "skeleton_dag.py",
            "has_py": True
        },
        {
            "stage": "STAGE 6",
            "icon": "📊",
            "title": "Power BI Control Tower (Explainer)",
            "md_path": STUDY_PACK_DIR / "06_POWER_BI_CONTROL_TOWER" / "EXPLAINER.md",
            "html_path": STUDY_PACK_DIR / "06_POWER_BI_CONTROL_TOWER" / "EXPLAINER.html",
            "html_rel": "06_POWER_BI_CONTROL_TOWER/EXPLAINER.html",
            "has_py": False
        },
        {
            "stage": "STAGE 6-B",
            "icon": "🖼️",
            "title": "Power BI Step-by-Step Build Guide",
            "md_path": STUDY_PACK_DIR / "06_POWER_BI_CONTROL_TOWER" / "POWERBI_STEP_BY_STEP_BUILD_GUIDE.md",
            "html_path": STUDY_PACK_DIR / "06_POWER_BI_CONTROL_TOWER" / "POWERBI_STEP_BY_STEP_BUILD_GUIDE.html",
            "html_rel": "06_POWER_BI_CONTROL_TOWER/POWERBI_STEP_BY_STEP_BUILD_GUIDE.html",
            "has_py": False
        },
        {
            "stage": "STAGE 7",
            "icon": "🎯",
            "title": "Master Interview Q&A (19 Core Questions)",
            "md_path": STUDY_PACK_DIR / "07_INTERVIEW_DEFENSE_QA" / "TOP_INTERVIEW_QUESTIONS.md",
            "html_path": STUDY_PACK_DIR / "07_INTERVIEW_DEFENSE_QA" / "TOP_INTERVIEW_QUESTIONS.html",
            "html_rel": "07_INTERVIEW_DEFENSE_QA/TOP_INTERVIEW_QUESTIONS.html",
            "has_py": False
        },
        {
            "stage": "STAGE 8",
            "icon": "💻",
            "title": "Streamlit Operations Console & Live Control Hub",
            "md_path": STUDY_PACK_DIR / "08_STREAMLIT_OPERATIONS_HUB" / "EXPLAINER.md",
            "html_path": STUDY_PACK_DIR / "08_STREAMLIT_OPERATIONS_HUB" / "EXPLAINER.html",
            "html_rel": "08_STREAMLIT_OPERATIONS_HUB/EXPLAINER.html",
            "skeleton": STUDY_PACK_DIR / "08_STREAMLIT_OPERATIONS_HUB" / "skeleton_app.py",
            "has_py": True
        },
        {
            "stage": "OVERVIEW",
            "icon": "📖",
            "title": "Study Pack Overview & Syllabus",
            "md_path": STUDY_PACK_DIR / "README.md",
            "html_path": STUDY_PACK_DIR / "README.html",
            "html_rel": "README.html",
            "has_py": False
        }
    ]

    total = len(modules)
    for i, mod in enumerate(modules):
        prev_link = f"../{modules[i-1]['html_rel']}" if i > 0 else None
        next_link = f"../{modules[i+1]['html_rel']}" if i < total - 1 else None
        skeleton = mod.get("skeleton")
        convert_md_to_html(mod["md_path"], mod["html_path"], prev_link, next_link, skeleton)

    print("\n[SUCCESS] All individual HTML documents successfully updated with Light/Dark Mode!")

if __name__ == "__main__":
    build_all()
