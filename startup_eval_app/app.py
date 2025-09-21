#!/usr/bin/env python3
import os
import gradio as gr
from utils import db
from utils.pdf_parser import parse_pdf
from utils.charting import plot_profit_loss, plot_funding_vs_valuation
from utils.orchestrator import run_multi_agent_analysis

db.init_db(os.path.join("data", "startups.db"))
APP_TITLE = "🚀 AI Analysts for Startup Evaluation"
INTRO = (
    "Upload pitch decks (PDF), search, and select a startup to see its dashboard. "
    "The navbar turns green if our multi-agent system recommends a Good Deal (top 5 reasons), "
    "otherwise red with reasons why not."
)

def refresh_dropdown():
    items = db.list_startups()
    return [gr.Dropdown(choices=[f"{i['name']} (#{i['id']})" for i in items], interactive=True)]

def add_startup(name, pdf_files):
    if not name or not pdf_files:
        return "❌ Please provide both a name and a PDF.", *refresh_dropdown()
    try:
        parsed_text = ""
        for pdf_file in pdf_files:
            parsed_text += parse_pdf(pdf_file.name)
    except Exception as e:
        parsed_text = f"[Parser failed: {e}]"
    sid = db.add_startup(name=name, description=parsed_text)
    return f"✅ Added startup '{name}' (id={sid}).", *refresh_dropdown()

def search_startups(query):
    results = db.search_startups(query or "")
    if not results:
        return "No results."
    lines = [f"#{r['id']}: {r['name']}" for r in results]
    return "\n".join(lines)

def parse_startup_id(drop_label):
    try:
        return int(drop_label.split("#")[-1].rstrip(")"))
    except Exception:
        return -1

def show_dashboard(selected_label):
    sid = parse_startup_id(selected_label)
    if sid <= 0:
        return (gr.Markdown.update(value="Select a valid startup."),
                gr.HighlightedText.update(value=[]),
                gr.Plot.update(None),
                gr.Plot.update(None),
                gr.TextArea.update(None))
    startup = db.get_startup(sid)
    analysis = run_multi_agent_analysis(startup)

    good = analysis.get("is_good", False)
    badge = "🟢 GOOD DEAL" if good else "🔴 BAD DEAL"
    color = "#0ea55b" if good else "#ef4444"
    navbar_md = f"<div style='padding:8px;border-radius:8px;background:{color};color:white;font-weight:700'>{badge}</div>"

    reasons = analysis.get("top_reasons", []) or ["It is not a good invetment given the current market trend."]
    reasons_pairs = [(r, f"reason_{i}") for i, r in enumerate(reasons, 1)]

    profits = startup.get("profits") or [10, -5, 15, 22, -3, 30]
    funding = startup.get("funding") or [1, 2, 5, 8, 13, 21]
    valuation = startup.get("valuation") or [f * 12 for f in funding]

    fig1 = plot_profit_loss(profits)
    fig2 = plot_funding_vs_valuation(funding, valuation)

    return gr.Markdown(value=navbar_md), gr.HighlightedText(value=reasons_pairs), fig1, fig2, gr.TextArea(value=analysis, lines=30)

with gr.Blocks(css="footer {visibility: hidden}") as demo:
    gr.Markdown(f"# {APP_TITLE}")
    gr.Markdown(INTRO)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### ➕ Add Startup")
            name_in = gr.Textbox(label="Startup Name", placeholder="Acme AI")
            pdf_in = gr.File(file_count="multiple", label="Upload Pitch Deck / PDF", file_types=[".pdf"])
            add_btn = gr.Button("Add")
            add_status = gr.Textbox(label="Status", interactive=False)

            add_btn.click(add_startup, [name_in, pdf_in], [add_status,]).then(
                refresh_dropdown, outputs=[]
            )

            # gr.Markdown("### 🔎 Search")
            # query = gr.Textbox(label="Query", placeholder="language model, fintech, 2024...")
            # search_btn = gr.Button("Search")
            # search_out = gr.Textbox(label="Results", lines=8)

            # search_btn.click(search_startups, [query], [search_out])

        with gr.Column(scale=1):
            gr.Markdown("### 📋 Select Startup")
            dd = gr.Dropdown(label="Startups", choices=[f"{i['name']} (#{i['id']})" for i in db.list_startups()], interactive=True)
            go = gr.Button("Open Dashboard")

            gr.Markdown("### 📊 Dashboard")
            navbar = gr.Markdown()
            reasons = gr.HighlightedText(label="Top Reasons")
            chart1 = gr.Plot(label="Profit / Loss Over Time")
            chart2 = gr.Plot(label="Funding vs Valuation")
            analysis = gr.TextArea(label="Analysis", lines=30)

            go.click(show_dashboard, [dd], [navbar, reasons, chart1, chart2, analysis])

if __name__ == "__main__":
    demo.launch()
