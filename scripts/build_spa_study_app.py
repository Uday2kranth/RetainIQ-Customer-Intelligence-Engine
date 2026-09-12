#!/usr/bin/env python3
"""
RetainIQ: Single-Page Mobile Web App (SPA) Generator
Compiles all 9 study modules, explainers, Python skeletons, interview Q&As,
and Power BI screenshots into ONE SINGLE self-contained HTML file.
Includes:
- Dynamic Light/Dark Mode toggle with local storage persistence
- Mobile thumb navigation
- Smooth animations and zero-external-dependency rendering
"""

import os
import re
import base64
import mimetypes
from pathlib import Path
import markdown

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXTERNAL_STUDY_PACK = Path(r"D:\important_cmd_history\study_pack")
STUDY_PACK_DIR = EXTERNAL_STUDY_PACK if EXTERNAL_STUDY_PACK.exists() else PROJECT_ROOT / "study_pack"

SPA_CSS = """
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
  -webkit-tap-highlight-color: transparent;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.65;
  font-size: 16px;
  padding-bottom: 95px; /* Space for sticky bottom tab bar on mobile */
}

/* Sticky App Header */
header.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: 0.75rem 1rem 0.5rem;
  box-shadow: 0 4px 20px var(--shadow-color);
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 900px;
  margin: 0 auto;
}

.app-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--accent-cyan);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-actions {
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
  transition: all 0.2s;
}

.theme-toggle-btn:hover {
  border-color: var(--accent-cyan);
  color: var(--accent-cyan);
}

.app-badge {
  background: rgba(74, 222, 128, 0.15);
  color: var(--accent-green);
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid rgba(74, 222, 128, 0.3);
}

/* Horizontal Scrollable Tab Bar */
.tab-scroller {
  display: flex;
  overflow-x: auto;
  gap: 0.5rem;
  padding: 0.6rem 0 0.2rem;
  max-width: 900px;
  margin: 0 auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.tab-scroller::-webkit-scrollbar {
  display: none;
}

.tab-btn {
  flex: 0 0 auto;
  background: var(--bg-card);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 0.45rem 0.9rem;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background: var(--accent-cyan);
  color: #0b0f19;
  border-color: var(--accent-cyan);
  box-shadow: 0 0 15px rgba(56, 189, 248, 0.35);
}

/* Main Container */
main.content-container {
  max-width: 900px;
  margin: 1.5rem auto;
  padding: 0 1rem;
}

/* Section Switching */
.study-section {
  display: none;
  animation: fadeIn 0.25s ease-in-out;
}

.study-section.active {
  display: block;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Headings & Text */
h1, h2, h3, h4 {
  color: var(--text-primary);
  font-weight: 700;
  line-height: 1.3;
  margin-top: 1.8rem;
  margin-bottom: 0.8rem;
}

h1 {
  font-size: 1.8rem;
  color: var(--accent-cyan);
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 0.5rem;
  margin-top: 0.5rem;
}

h2 {
  font-size: 1.4rem;
  color: var(--accent-blue);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.35rem;
}

h3 {
  font-size: 1.15rem;
  color: var(--text-primary);
}

p {
  margin-bottom: 1.1rem;
  color: var(--text-secondary);
}

/* Blockquotes / Voice Alerts */
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

/* Code Blocks */
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

/* Section Bottom Navigation */
.section-nav-footer {
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.btn-nav-step {
  padding: 0.7rem 1.4rem;
  background: var(--bg-card);
  color: var(--accent-cyan);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-nav-step:hover {
  background: rgba(56, 189, 248, 0.15);
  border-color: var(--accent-cyan);
}

.btn-nav-step.primary {
  background: var(--accent-cyan);
  color: #0b0f19;
  border-color: var(--accent-cyan);
}

/* Code Skeleton Card */
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

/* Bottom Floating Tab Pill for Mobile */
.mobile-bottom-bar {
  position: fixed;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 999;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 30px;
  padding: 0.4rem 0.8rem;
  display: flex;
  gap: 0.6rem;
  box-shadow: 0 10px 30px var(--shadow-color);
}

.mobile-bottom-btn {
  background: transparent;
  border: none;
  color: var(--accent-cyan);
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  padding: 0.4rem 0.6rem;
  border-radius: 20px;
}

.mobile-bottom-btn:hover {
  background: rgba(56, 189, 248, 0.15);
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

def inline_images(md_content: str, base_dir: Path) -> str:
    def replace_img(match):
        alt = match.group(1)
        img_rel = match.group(2)
        if img_rel.startswith("http") or img_rel.startswith("data:"):
            return match.group(0)
        clean_rel = img_rel.replace("./", "").replace("/", os.sep)
        local_path = (base_dir / clean_rel).resolve()
        if local_path.exists():
            data_uri = image_to_base64(local_path)
            return f"![{alt}]({data_uri})"
        return match.group(0)
    return re.sub(r"!\[(.*?)\]\((.*?)\)", replace_img, md_content)

def build_spa():
    print("[*] Building RetainIQ Single-Page Application (SPA) with Light/Dark Mode...")

    modules = [
        {
            "id": "sec-cheat-sheet",
            "nav_label": "🚀 Cheat Sheet",
            "icon": "🚀",
            "title": "Quick-Run & Defense Cheat Sheet",
            "md_path": STUDY_PACK_DIR / "00_QUICK_RUN_&_DEFENSE_CHEAT_SHEET.md",
        },
        {
            "id": "sec-stage0",
            "nav_label": "⚡ Stage 0: Setup",
            "icon": "⚡",
            "title": "Stage 0: Setup & Launch",
            "md_path": STUDY_PACK_DIR / "00_SETUP_&_LAUNCH" / "HOW_TO_RUN_PROJECT.md",
        },
        {
            "id": "sec-stage1",
            "nav_label": "🗄️ Stage 1: SQL",
            "icon": "🗄️",
            "title": "Stage 1: SQL Database & Ingestion",
            "md_path": STUDY_PACK_DIR / "01_SQL_DATABASE_&_INGESTION" / "EXPLAINER.md",
            "skeleton": STUDY_PACK_DIR / "01_SQL_DATABASE_&_INGESTION" / "skeleton_ingest.py",
        },
        {
            "id": "sec-stage2",
            "nav_label": "📈 Stage 2: RFM",
            "icon": "📈",
            "title": "Stage 2: RFM Feature Engineering",
            "md_path": STUDY_PACK_DIR / "02_RFM_FEATURE_ENGINEERING" / "EXPLAINER.md",
            "skeleton": STUDY_PACK_DIR / "02_RFM_FEATURE_ENGINEERING" / "skeleton_rfm.py",
        },
        {
            "id": "sec-stage3",
            "nav_label": "🌲 Stage 3: ML",
            "icon": "🌲",
            "title": "Stage 3: Machine Learning Model",
            "md_path": STUDY_PACK_DIR / "03_MACHINE_LEARNING_MODEL" / "EXPLAINER.md",
            "skeleton": STUDY_PACK_DIR / "03_MACHINE_LEARNING_MODEL" / "skeleton_model.py",
        },
        {
            "id": "sec-stage4",
            "nav_label": "📬 Stage 4: Alerts",
            "icon": "📬",
            "title": "Stage 4: Gmail OAuth 2.0 Alerts",
            "md_path": STUDY_PACK_DIR / "04_GMAIL_OAUTH_ALERTS" / "EXPLAINER.md",
            "skeleton": STUDY_PACK_DIR / "04_GMAIL_OAUTH_ALERTS" / "skeleton_alert.py",
        },
        {
            "id": "sec-stage5",
            "nav_label": "🌪️ Stage 5: Airflow",
            "icon": "🌪️",
            "title": "Stage 5: Apache Airflow Orchestration",
            "md_path": STUDY_PACK_DIR / "05_APACHE_AIRFLOW" / "EXPLAINER.md",
            "skeleton": STUDY_PACK_DIR / "05_APACHE_AIRFLOW" / "skeleton_dag.py",
        },
        {
            "id": "sec-stage6",
            "nav_label": "📊 Stage 6: Power BI",
            "icon": "📊",
            "title": "Stage 6: Power BI Control Tower",
            "md_path": STUDY_PACK_DIR / "06_POWER_BI_CONTROL_TOWER" / "EXPLAINER.md",
        },
        {
            "id": "sec-stage6b",
            "nav_label": "🖼️ PBI Build Guide",
            "icon": "🖼️",
            "title": "Power BI Step-by-Step Visual Build Manual",
            "md_path": STUDY_PACK_DIR / "06_POWER_BI_CONTROL_TOWER" / "POWERBI_STEP_BY_STEP_BUILD_GUIDE.md",
        },
        {
            "id": "sec-stage7",
            "nav_label": "🎯 Stage 7: Q&A",
            "icon": "🎯",
            "title": "Stage 7: Master Interview Defense Q&A",
            "md_path": STUDY_PACK_DIR / "07_INTERVIEW_DEFENSE_QA" / "TOP_INTERVIEW_QUESTIONS.md",
        },
        {
            "id": "sec-stage8",
            "nav_label": "💻 Stage 8: Hub",
            "icon": "💻",
            "title": "Stage 8: Streamlit Operations Console & Live Control Hub",
            "md_path": STUDY_PACK_DIR / "08_STREAMLIT_OPERATIONS_HUB" / "EXPLAINER.md",
            "skeleton": STUDY_PACK_DIR / "08_STREAMLIT_OPERATIONS_HUB" / "skeleton_app.py",
        },
    ]

    # Build navigation tab buttons
    nav_tabs_html = []
    for idx, mod in enumerate(modules):
        active_cls = "active" if idx == 0 else ""
        nav_tabs_html.append(
            f'<button class="tab-btn {active_cls}" data-target="{mod["id"]}" onclick="switchSection(\'{mod["id"]}\')">{mod["nav_label"]}</button>'
        )

    # Build sections
    sections_html = []
    total_mods = len(modules)
    for idx, mod in enumerate(modules):
        active_cls = "active" if idx == 0 else ""
        with open(mod["md_path"], "r", encoding="utf-8") as f:
            md_text = f.read()

        md_text = inline_images(md_text, mod["md_path"].parent)
        body_html = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'nl2br'])
        body_html = re.sub(r"(<table>[\s\S]*?<\/table>)", r'<div class="table-container">\1</div>', body_html)

        # Skeleton code card
        skeleton_html = ""
        if "skeleton" in mod and mod["skeleton"].exists():
            with open(mod["skeleton"], "r", encoding="utf-8") as sf:
                code_text = sf.read()
            skeleton_html = f"""
            <div class="code-skeleton-card">
              <div class="code-skeleton-header">
                <span>💻 25-Line Code Skeleton ({mod["skeleton"].name})</span>
                <span class="app-badge">Pure Python</span>
              </div>
              <pre><code>{code_text}</code></pre>
            </div>
            """

        # Next / Prev buttons
        prev_id = modules[idx - 1]["id"] if idx > 0 else None
        next_id = modules[idx + 1]["id"] if idx < total_mods - 1 else None

        prev_btn = f'<button class="btn-nav-step" onclick="switchSection(\'{prev_id}\')">← {modules[idx-1]["nav_label"]}</button>' if prev_id else '<span></span>'
        next_btn = f'<button class="btn-nav-step primary" onclick="switchSection(\'{next_id}\')">{modules[idx+1]["nav_label"]} →</button>' if next_id else '<span></span>'

        sections_html.append(f"""
        <section id="{mod['id']}" class="study-section {active_cls}">
          {body_html}
          {skeleton_html}
          <div class="section-nav-footer">
            {prev_btn}
            {next_btn}
          </div>
        </section>
        """)

    tabs_str = "\n".join(nav_tabs_html)
    sections_str = "\n".join(sections_html)

    full_app_html = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>RetainIQ: Defense Study App (Light & Dark Mode)</title>
  {THEME_SCRIPT}
  <style>
    {SPA_CSS}
  </style>
</head>
<body>
  <!-- Sticky Header -->
  <header class="app-header">
    <div class="header-top">
      <div class="app-title">
        <span>🚀</span> RetainIQ Defense Hub
      </div>
      <div class="header-actions">
        <button class="theme-toggle-btn" onclick="toggleTheme()" aria-label="Toggle Light/Dark Theme">
          <span id="themeIcon">🌙</span> <span id="themeText">Dark</span>
        </button>
        <span class="app-badge">SPA</span>
      </div>
    </div>
    <div class="tab-scroller" id="tabScroller">
      {tabs_str}
    </div>
  </header>

  <!-- Main Content Sections -->
  <main class="content-container">
    {sections_str}
  </main>

  <!-- Mobile Floating Bottom Bar -->
  <div class="mobile-bottom-bar">
    <button class="mobile-bottom-btn" onclick="prevSection()">◀ Prev</button>
    <button class="mobile-bottom-btn" style="color: var(--accent-green);" onclick="switchSection('sec-cheat-sheet')">⚡ Cheat Sheet</button>
    <button class="mobile-bottom-btn" style="color: var(--accent-amber);" onclick="switchSection('sec-stage7')">🎯 Q&A</button>
    <button class="mobile-bottom-btn" onclick="nextSection()">Next ▶</button>
  </div>

  <script>
    const sectionIds = {list(m['id'] for m in modules)};
    let currentIndex = 0;

    function switchSection(targetId) {{
      const targetSec = document.getElementById(targetId);
      if (!targetSec) return;

      currentIndex = sectionIds.indexOf(targetId);

      // Toggle sections
      document.querySelectorAll('.study-section').forEach(sec => sec.classList.remove('active'));
      targetSec.classList.add('active');

      // Toggle tab buttons
      document.querySelectorAll('.tab-btn').forEach(btn => {{
        if (btn.getAttribute('data-target') === targetId) {{
          btn.classList.add('active');
          btn.scrollIntoView({{ behavior: 'smooth', block: 'nearest', inline: 'center' }});
        }} else {{
          btn.classList.remove('active');
        }}
      }});

      // Scroll to top
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function nextSection() {{
      if (currentIndex < sectionIds.length - 1) {{
        switchSection(sectionIds[currentIndex + 1]);
      }}
    }}

    function prevSection() {{
      if (currentIndex > 0) {{
        switchSection(sectionIds[currentIndex - 1]);
      }}
    }}
  </script>
</body>
</html>
"""

    out_file = STUDY_PACK_DIR / "study_app.html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(full_app_html)
    print(f"[+] Successfully generated Single-Page App: {out_file}")

    # Copy to external study pack folder
    ext_file = Path(r"D:\important_cmd_history\study_pack\study_app.html")
    with open(ext_file, "w", encoding="utf-8") as f:
        f.write(full_app_html)
    print(f"[+] Synced to external study pack: {ext_file}")

    # Also update index.html to match
    ext_index = Path(r"D:\important_cmd_history\study_pack\index.html")
    with open(ext_index, "w", encoding="utf-8") as f:
        f.write(full_app_html)
    print(f"[+] Synced to external index.html: {ext_index}")

if __name__ == "__main__":
    build_spa()
