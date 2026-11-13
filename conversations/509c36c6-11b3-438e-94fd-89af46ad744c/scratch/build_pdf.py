import os
import subprocess
import markdown

md_path = r"C:\Users\Lenovo\.gemini\antigravity\brain\509c36c6-11b3-438e-94fd-89af46ad744c\whatsapp_message_scheduler_master_plan.md"
html_path = r"C:\Users\Lenovo\teamwork_projects\whatsapp_scheduler_bot\WhatsApp_Scheduler_Master_Technical_Plan.html"
pdf_path = r"C:\Users\Lenovo\teamwork_projects\whatsapp_scheduler_bot\WhatsApp_Scheduler_Master_Technical_Plan.pdf"
artifact_pdf_path = r"C:\Users\Lenovo\.gemini\antigravity\brain\509c36c6-11b3-438e-94fd-89af46ad744c\WhatsApp_Scheduler_Master_Technical_Plan.pdf"

with open(md_path, "r", encoding="utf-8") as f:
    text = f.read()

# Enable extensions for tables, fenced code, etc.
html_body = markdown.markdown(
    text,
    extensions=[
        'tables',
        'fenced_code',
        'codehilite',
        'toc',
        'attr_list'
    ]
)

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>WhatsApp In-App Message Scheduler Chatbot - Master Technical Plan</title>
<style>
  @page {{
    size: A4;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-right {{
      content: counter(page);
    }}
  }}
  
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1f2937;
    background: #ffffff;
    line-height: 1.6;
    font-size: 13px;
    margin: 0;
    padding: 0;
  }}

  h1 {{
    font-size: 26px;
    font-weight: 800;
    color: #0f172a;
    border-bottom: 3px solid #2563eb;
    padding-bottom: 8px;
    margin-top: 0;
    margin-bottom: 6px;
  }}

  h2 {{
    font-size: 18px;
    font-weight: 700;
    color: #1e3a8a;
    border-bottom: 1.5px solid #e2e8f0;
    padding-bottom: 5px;
    margin-top: 24px;
    margin-bottom: 12px;
    page-break-after: avoid;
  }}

  h3 {{
    font-size: 14.5px;
    font-weight: 600;
    color: #1e293b;
    margin-top: 16px;
    margin-bottom: 8px;
    page-break-after: avoid;
  }}

  p, li {{
    color: #334155;
    margin-bottom: 8px;
  }}

  ul, ol {{
    padding-left: 20px;
    margin-top: 4px;
    margin-bottom: 12px;
  }}

  hr {{
    border: 0;
    height: 1px;
    background: #e2e8f0;
    margin: 20px 0;
  }}

  /* Tables */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 11.5px;
    page-break-inside: avoid;
  }}

  th {{
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 600;
    text-align: left;
    padding: 8px 10px;
    border: 1px solid #cbd5e1;
  }}

  td {{
    padding: 7px 10px;
    border: 1px solid #e2e8f0;
    color: #334155;
  }}

  tr:nth-child(even) td {{
    background-color: #f8fafc;
  }}

  /* Code Blocks & Pre */
  pre {{
    background-color: #0f172a;
    color: #e2e8f0;
    padding: 12px 14px;
    border-radius: 6px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    font-size: 11px;
    line-height: 1.45;
    overflow-x: auto;
    page-break-inside: avoid;
    margin: 12px 0;
    border: 1px solid #1e293b;
  }}

  code {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    font-size: 11.5px;
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 2px 5px;
    border-radius: 4px;
  }}

  pre code {{
    background-color: transparent;
    color: inherit;
    padding: 0;
    font-size: 11px;
  }}

  /* Callouts & Badges */
  .badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
  }}

  blockquote {{
    border-left: 4px solid #2563eb;
    margin: 12px 0;
    padding: 8px 14px;
    background-color: #eff6ff;
    color: #1e40af;
    border-radius: 0 4px 4px 0;
    font-size: 12.5px;
  }}

  /* Header Box */
  .doc-header {{
    background: linear-gradient(135deg, #1e3a8a 0%, #0284c7 100%);
    color: #ffffff;
    padding: 20px 24px;
    border-radius: 8px;
    margin-bottom: 24px;
  }}

  .doc-header h1 {{
    color: #ffffff;
    border-bottom: none;
    margin-bottom: 6px;
  }}

  .doc-header .subtitle {{
    font-size: 15px;
    color: #bae6fd;
    font-weight: 500;
  }}

  .doc-header .meta {{
    margin-top: 14px;
    font-size: 11.5px;
    color: #e0f2fe;
    display: flex;
    gap: 20px;
    border-top: 1px solid rgba(255,255,255,0.2);
    padding-top: 10px;
  }}

  /* Avoid breakages */
  .keep-together {{
    page-break-inside: avoid;
  }}
</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
  mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
</script>
</head>
<body>

<div class="doc-header">
  <h1>WhatsApp In-App Message Scheduler Chatbot</h1>
  <div class="subtitle">Master Architectural Specification & Implementation Blueprint</div>
  <div class="meta">
    <span><strong>Target:</strong> Production Engineering Plan</span>
    <span><strong>Platform:</strong> WhatsApp Business API / Baileys Client</span>
    <span><strong>Date:</strong> November 2026</span>
    <span><strong>Status:</strong> Approved Architecture</span>
  </div>
</div>

{html_body}

</body>
</html>
"""

# Replace mermaid code blocks with mermaid div if present
html_template = html_template.replace('<pre><code class="language-mermaid">', '<div class="mermaid">')
html_template = html_template.replace('<pre><code class="mermaid">', '<div class="mermaid">')
html_template = html_template.replace('</code></pre>', '</div>')

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"Generated HTML at: {html_path}")

# Run headless Chrome to produce PDF
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(chrome_path):
    chrome_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

cmd = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    "--run-all-compositor-stages-before-draw",
    f"--print-to-pdf={pdf_path}",
    html_path
]

print("Executing Chrome headless print-to-pdf...")
result = subprocess.run(cmd, capture_output=True, text=True)
print(f"Chrome return code: {result.returncode}")

if os.path.exists(pdf_path):
    import shutil
    shutil.copy2(pdf_path, artifact_pdf_path)
    size_kb = os.path.getsize(pdf_path) / 1024
    print(f"Successfully generated PDF: {pdf_path} ({size_kb:.1f} KB)")
    print(f"Copied to artifact directory: {artifact_pdf_path}")
else:
    print("PDF generation failed.")
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
