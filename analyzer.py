from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "with",
}


SECTION_PATTERNS = {
    "abstract": re.compile(r"^\s*abstract\s*$", re.IGNORECASE),
    "introduction": re.compile(r"^\s*(\d+\.?\s+)?introduction\s*$", re.IGNORECASE),
    "methodology": re.compile(
        r"^\s*(\d+\.?\s+)?(method|methods|methodology|approach)\s*$",
        re.IGNORECASE,
    ),
    "results": re.compile(
        r"^\s*(\d+\.?\s+)?(result|results|findings|evaluation)\s*$",
        re.IGNORECASE,
    ),
    "conclusion": re.compile(
        r"^\s*(\d+\.?\s+)?(conclusion|conclusions|discussion|summary)\s*$",
        re.IGNORECASE,
    ),
}


@dataclass
class DocumentReport:
    title: str
    document_type: str
    page_count: int
    word_count: int
    summary: list[str]
    key_sections: list[str]
    evidence_points: list[str]
    numeric_highlights: list[str]
    audience: str
    risks_or_gaps: list[str]
    follow_up_questions: list[str]
    preview_text: str


def read_pdf_text(pdf_path: str | Path) -> tuple[str, int]:
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        pages.append((page.extract_text() or "").strip())
    text = "\n\n".join(page for page in pages if page)
    return normalize_text(text), len(reader.pages)


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    text = text.replace("\n", " ")
    candidates = re.split(r"(?<=[.!?])\s+", text)
    return [clean_sentence(s) for s in candidates if len(clean_sentence(s)) >= 40]


def clean_sentence(sentence: str) -> str:
    sentence = re.sub(r"\s+", " ", sentence).strip(" -")
    return sentence


def extract_title(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    candidates = []
    for line in lines[:20]:
        if len(line.split()) < 4:
            continue
        if len(line) > 180:
            continue
        if re.search(r"(abstract|introduction|www\.|http)", line, re.IGNORECASE):
            continue
        score = len(line)
        if line == line.title():
            score += 15
        if not line.endswith((".", ":", ";")):
            score += 10
        candidates.append((score, line))
    return max(candidates, default=(0, "Untitled Document"))[1]


def classify_document(text: str) -> str:
    lower = text.lower()
    research_signals = sum(
        1
        for token in ["abstract", "method", "results", "conclusion", "references"]
        if token in lower
    )
    brochure_signals = sum(
        1
        for token in ["contact", "call us", "features", "benefits", "pricing", "overview"]
        if token in lower
    )
    if research_signals >= brochure_signals and research_signals >= 2:
        return "Research Paper"
    if brochure_signals >= 2:
        return "Brochure / Marketing Collateral"
    return "General PDF Document"


def extract_sections(text: str) -> list[str]:
    section_names = []
    for line in text.splitlines():
        candidate = line.strip()
        if not candidate or len(candidate.split()) > 8:
            continue
        for label, pattern in SECTION_PATTERNS.items():
            if pattern.match(candidate):
                pretty = label.capitalize()
                if pretty not in section_names:
                    section_names.append(pretty)
    return section_names[:8]


def build_frequency_index(sentences: list[str]) -> Counter:
    counts: Counter[str] = Counter()
    for sentence in sentences:
        words = re.findall(r"[A-Za-z][A-Za-z\-]{2,}", sentence.lower())
        for word in words:
            if word not in STOPWORDS:
                counts[word] += 1
    return counts


def rank_sentences(sentences: list[str], frequency_index: Counter) -> list[str]:
    scored: list[tuple[float, str]] = []
    for sentence in sentences:
        words = re.findall(r"[A-Za-z][A-Za-z\-]{2,}", sentence.lower())
        unique_words = {word for word in words if word not in STOPWORDS}
        if not unique_words:
            continue
        score = sum(frequency_index[word] for word in unique_words) / math.sqrt(len(unique_words))
        if re.search(r"\d", sentence):
            score += 1.2
        if 50 <= len(sentence) <= 220:
            score += 1.0
        scored.append((score, sentence))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [sentence for _, sentence in scored]


def pick_non_overlapping(sentences: list[str], limit: int) -> list[str]:
    selected: list[str] = []
    seen_terms: set[str] = set()
    for sentence in sentences:
        terms = {
            word
            for word in re.findall(r"[A-Za-z][A-Za-z\-]{3,}", sentence.lower())
            if word not in STOPWORDS
        }
        if terms and len(terms & seen_terms) / max(len(terms), 1) > 0.7:
            continue
        selected.append(sentence)
        seen_terms.update(terms)
        if len(selected) >= limit:
            break
    return selected


def extract_numeric_highlights(text: str) -> list[str]:
    snippets = []
    for sentence in split_sentences(text):
        if re.search(r"\d", sentence):
            snippets.append(sentence)
    unique = []
    for snippet in snippets:
        if snippet not in unique:
            unique.append(snippet)
    return unique[:6]


def infer_audience(text: str, document_type: str) -> str:
    lower = text.lower()
    if document_type == "Research Paper":
        return "Researchers, technical reviewers, and stakeholders evaluating methodology or results."
    if any(token in lower for token in ["customer", "buyers", "business", "enterprise"]):
        return "Prospective customers or decision-makers assessing the offering."
    return "General readers who need a structured understanding of the document."


def infer_risks(text: str, sections: list[str], numeric_highlights: list[str]) -> list[str]:
    risks = []
    lower = text.lower()
    if "references" not in lower and "bibliography" not in lower:
        risks.append("The document does not clearly expose references or source citations.")
    if "results" in sections and not numeric_highlights:
        risks.append("Results are mentioned but quantified outcomes are not obvious in extracted text.")
    if len(text.split()) < 400:
        risks.append("The source text is short, which limits the depth of evidence extraction.")
    if "contact" not in lower and "email" not in lower and "phone" not in lower:
        risks.append("No explicit contact or ownership details were detected.")
    return risks[:4] or ["No major structural risks were detected from the extracted text."]


def build_follow_up_questions(document_type: str, sections: list[str], numeric_highlights: list[str]) -> list[str]:
    questions = []
    if document_type == "Research Paper":
        questions.append("What assumptions or dataset constraints most affect the reported results?")
        questions.append("Which result should be independently validated first?")
    else:
        questions.append("Which claims in the document are supported by direct evidence or measured outcomes?")
        questions.append("What decision is this document trying to influence?")
    if "Methodology" not in sections:
        questions.append("What process or method produced the conclusions in this document?")
    if not numeric_highlights:
        questions.append("What quantifiable facts should be added to strengthen credibility?")
    return questions[:4]


def build_preview(report: DocumentReport) -> str:
    lines = [
        f"Title: {report.title}",
        f"Type: {report.document_type}",
        f"Pages: {report.page_count}",
        f"Words: {report.word_count}",
        "",
        "Executive Summary:",
    ]
    lines.extend(f"- {item}" for item in report.summary)
    lines.append("")
    lines.append("Key Evidence:")
    lines.extend(f"- {item}" for item in report.evidence_points)
    return "\n".join(lines)


def analyze_pdf(pdf_path: str | Path) -> DocumentReport:
    text, page_count = read_pdf_text(pdf_path)
    sentences = split_sentences(text)
    frequency_index = build_frequency_index(sentences)
    ranked = rank_sentences(sentences, frequency_index)
    summary = pick_non_overlapping(ranked, 4)
    evidence = pick_non_overlapping([s for s in ranked if s not in summary], 5)
    numeric_highlights = extract_numeric_highlights(text)
    sections = extract_sections(text)
    title = extract_title(text)
    document_type = classify_document(text)
    audience = infer_audience(text, document_type)
    risks = infer_risks(text, sections, numeric_highlights)
    follow_up = build_follow_up_questions(document_type, sections, numeric_highlights)

    report = DocumentReport(
        title=title,
        document_type=document_type,
        page_count=page_count,
        word_count=len(text.split()),
        summary=summary or ["The document was extracted successfully, but the text provided limited summary candidates."],
        key_sections=sections or ["No standard sections were confidently detected."],
        evidence_points=evidence or ["No additional evidence statements were confidently extracted."],
        numeric_highlights=numeric_highlights or ["No strong numeric highlights were detected in the extracted text."],
        audience=audience,
        risks_or_gaps=risks,
        follow_up_questions=follow_up,
        preview_text="",
    )
    report.preview_text = build_preview(report)
    return report
