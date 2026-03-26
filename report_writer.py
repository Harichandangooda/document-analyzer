from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from analyzer import DocumentReport


def _styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#183153"),
            alignment=TA_LEFT,
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1F4E79"),
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyCopy",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            spaceAfter=4,
        )
    )
    return styles


def _bullet_lines(items: list[str], styles) -> list[Paragraph]:
    return [Paragraph(f"&bull; {item}", styles["BodyCopy"]) for item in items]


def build_report_pdf(report: DocumentReport, source_pdf: str | Path, output_pdf: str | Path) -> str:
    styles = _styles()
    output_path = Path(output_pdf)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=LETTER,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
    )

    summary_table = Table(
        [
            ["Source File", Path(source_pdf).name],
            ["Document Type", report.document_type],
            ["Pages", str(report.page_count)],
            ["Word Count", str(report.word_count)],
            ["Primary Audience", report.audience],
        ],
        colWidths=[1.6 * inch, 4.9 * inch],
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF1F8")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1D1D1D")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#B8C7D9")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8C7D9")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story = [
        Paragraph("Document Analysis Report", styles["ReportTitle"]),
        Paragraph(report.title, styles["SectionTitle"]),
        summary_table,
        Spacer(1, 0.18 * inch),
        Paragraph("Harness Profile", styles["SectionTitle"]),
        Paragraph(
            "This report uses a fixed analysis harness: normalized PDF extraction, rule-based section detection, "
            "deterministic sentence ranking, and a stable report template. The structure is intentionally constrained "
            "to keep repeated runs consistent.",
            styles["BodyCopy"],
        ),
        Paragraph("Executive Summary", styles["SectionTitle"]),
        *_bullet_lines(report.summary, styles),
        Paragraph("Detected Sections", styles["SectionTitle"]),
        *_bullet_lines(report.key_sections, styles),
        Paragraph("Key Evidence", styles["SectionTitle"]),
        *_bullet_lines(report.evidence_points, styles),
        Paragraph("Numeric Highlights", styles["SectionTitle"]),
        *_bullet_lines(report.numeric_highlights, styles),
        Paragraph("Risks And Gaps", styles["SectionTitle"]),
        *_bullet_lines(report.risks_or_gaps, styles),
        Paragraph("Follow-Up Questions", styles["SectionTitle"]),
        *_bullet_lines(report.follow_up_questions, styles),
    ]

    doc.build(story)
    return str(output_path)
