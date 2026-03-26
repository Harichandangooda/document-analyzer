# Deterministic PDF Document Analyzer

A Gradio application that accepts a PDF, analyzes its extracted text through a fixed processing harness, and generates a downloadable PDF report.

The current implementation is aimed at text-based PDFs such as:

- Research papers
- Brochures
- General informational PDFs

## Objective

The project is built to avoid unstable, open-ended output generation. Instead of producing random or highly variable responses, it uses a constrained analysis flow with a fixed report schema so the same source document produces the same structure and broadly the same result on repeated runs.

## Core Design Principle

This app uses Harness Engineering for consistency.

That means:

- The pipeline follows a fixed sequence of extraction, normalization, scoring, and report generation.
- The output report always uses the same section layout.
- Document interpretation is based on deterministic rules and heuristics.
- No free-form LLM generation is used in the current version.

## Features

- Upload a PDF through a Gradio interface
- Extract text from the PDF using `pypdf`
- Classify the document type using explicit rules
- Detect common sections such as Abstract, Introduction, Methodology, Results, and Conclusion
- Generate a structured summary and evidence list through deterministic sentence ranking
- Extract numeric highlights from the text
- Infer likely audience, risks, and follow-up questions
- Export a polished analysis report as a downloadable PDF

## Project Structure

- [app.py](C:/Users/chand/Downloads/projects_llm_ai/document_analyzer/app.py)
  Gradio app entrypoint. Handles file upload, invokes analysis, and returns the downloadable report.

- [analyzer.py](C:/Users/chand/Downloads/projects_llm_ai/document_analyzer/analyzer.py)
  Deterministic analysis pipeline. Responsible for PDF text extraction, normalization, classification, section detection, sentence ranking, and structured report assembly.

- [report_writer.py](C:/Users/chand/Downloads/projects_llm_ai/document_analyzer/report_writer.py)
  PDF report generator. Uses `reportlab` to render the final analysis report into a stable layout.

- [requirements.txt](C:/Users/chand/Downloads/projects_llm_ai/document_analyzer/requirements.txt)
  Python dependencies.

- [outputs/](C:/Users/chand/Downloads/projects_llm_ai/document_analyzer/outputs)
  Generated report PDFs are written here at runtime.

- [.gitignore](C:/Users/chand/Downloads/projects_llm_ai/document_analyzer/.gitignore)
  Ignores local environment folders, cache files, and generated outputs.

## How It Works

### 1. PDF Input

The user uploads a PDF through the Gradio interface.

### 2. Text Extraction

The app reads the PDF with `pypdf` and extracts text from each page.

### 3. Normalization

The extracted text is cleaned to reduce noise:

- null characters removed
- repeated whitespace normalized
- excessive line breaks collapsed

### 4. Deterministic Analysis

The analyzer then applies a fixed set of rules:

- title extraction from early candidate lines
- document type classification from keyword signals
- section detection through regex pattern matching
- sentence scoring using term-frequency-style weighting
- numeric highlight extraction from sentences containing digits
- risk and follow-up question generation from fixed rules

### 5. Report Generation

The structured analysis is written into a PDF report with the following sections:

- Document metadata
- Harness profile
- Executive summary
- Detected sections
- Key evidence
- Numeric highlights
- Risks and gaps
- Follow-up questions

## Why The Output Is Consistent

This implementation is intentionally constrained.

- The analyzer does not sample or improvise.
- The report schema is fixed.
- The sentence ranking logic is deterministic.
- The same input text is processed through the same rules each time.

This reduces variance and makes the tool suitable for repeatable document review workflows.

## Requirements

- Python 3.10+
- `uv` or `pip`

## Setup With uv

From the project root:

```bash
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
uv run python app.py
```

Alternative without activating the environment:

```bash
uv venv
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
uv run --python .venv\Scripts\python.exe python app.py
```

## Setup With pip

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Running The App

After startup, Gradio will expose a local URL in the terminal. Open it in a browser, upload a PDF, and click `Generate Report`.

The app returns:

- a text preview of the analysis
- a downloadable PDF report

## Output Format

The generated report includes:

- title
- document type
- page count
- word count
- audience
- executive summary
- key sections
- evidence points
- numeric highlights
- risks or gaps
- follow-up questions

## Current Limitations

- Best suited for text-based PDFs
- Scanned or image-only PDFs are not supported because OCR is not included
- Table-heavy layouts may produce imperfect extracted text
- Document classification is heuristic-based, not domain-trained

## Verification Performed

The code was syntax-checked with:

```bash
python -m py_compile app.py analyzer.py report_writer.py
```

## Next Possible Improvements

- Add OCR support for scanned PDFs
- Add stricter section extraction for academic papers
- Add configurable report templates
- Add evaluation tests with sample PDFs
- Add schema-validated LLM augmentation while keeping deterministic constraints

## Summary

This project provides a practical base for consistent PDF analysis with a simple UI and downloadable report generation. Its main value is not creativity; it is repeatability, structure, and predictable output.
