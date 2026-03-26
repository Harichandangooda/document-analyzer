from __future__ import annotations

from pathlib import Path

import gradio as gr

from analyzer import analyze_pdf
from report_writer import build_report_pdf


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def process_pdf(pdf_file: str) -> tuple[str, str]:
    if not pdf_file:
        raise gr.Error("Upload a PDF file to continue.")

    report = analyze_pdf(pdf_file)
    output_name = f"{Path(pdf_file).stem}_analysis_report.pdf"
    output_path = OUTPUT_DIR / output_name
    build_report_pdf(report, pdf_file, output_path)
    return report.preview_text, str(output_path)


with gr.Blocks(title="Deterministic PDF Document Analyzer") as demo:
    gr.Markdown(
        """
        # Deterministic PDF Document Analyzer
        Upload a research paper or brochure and get a downloadable analysis PDF.

        The app uses a fixed analysis harness instead of open-ended generation:
        - Stable report sections
        - Rule-based extraction
        - Deterministic sentence ranking
        - Repeatable PDF output formatting
        """
    )

    with gr.Row():
        pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"], type="filepath")
        report_output = gr.File(label="Download Report PDF")

    preview_output = gr.Textbox(
        label="Report Preview",
        lines=22,
        max_lines=28,
    )

    analyze_button = gr.Button("Generate Report", variant="primary")
    analyze_button.click(
        fn=process_pdf,
        inputs=[pdf_input],
        outputs=[preview_output, report_output],
    )


if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
