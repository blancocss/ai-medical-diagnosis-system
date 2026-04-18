"""
medical_report.py
=================
Generates a professional PDF medical diagnosis report using ReportLab.
Improvements over original:
  - Timestamped, sanitised filename (no path-traversal risk)
  - Better typography hierarchy (Title, Heading1, Normal)
  - Coloured section header rule
  - Proper error propagation so the GUI can show a clean message
  - Saves to user's Documents folder (or CWD if unavailable)
"""

import os
import re
import logging
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors

logger = logging.getLogger("MedicalApp")


# ── Helper: safe file path ────────────────────────────────────────────────────
def _safe_filename(patient_name: str) -> str:
    """Return a safe, timestamped PDF filename in the working directory."""
    # Strip anything that is not alphanumeric, space, hyphen, or underscore
    safe_name = re.sub(r"[^\w\s\-]", "", patient_name).strip().replace(" ", "_")
    safe_name = safe_name[:40] or "Patient"
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"Medical_Report_{safe_name}_{timestamp}.pdf"


# ── Custom paragraph styles ───────────────────────────────────────────────────
def _build_styles():
    base   = getSampleStyleSheet()
    styles = {}

    styles["title"] = ParagraphStyle(
        "ReportTitle",
        parent=base["Title"],
        fontSize=20,
        textColor=colors.HexColor("#1A56A0"),
        spaceAfter=6,
    )
    styles["section"] = ParagraphStyle(
        "SectionHead",
        parent=base["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#2E86C1"),
        spaceBefore=10,
        spaceAfter=4,
    )
    styles["body"] = ParagraphStyle(
        "BodyText",
        parent=base["Normal"],
        fontSize=11,
        leading=16,
        spaceAfter=4,
    )
    styles["value"] = ParagraphStyle(
        "ValueText",
        parent=base["Normal"],
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#2D3748"),
        leftIndent=12,
        spaceAfter=6,
    )
    return styles


# ── Main generation function ──────────────────────────────────────────────────
def generate_medical_report(
    patient_name:  str,
    disease:       str,
    arabic_disease: str,
    probability:   float,
    risk:          str,
    severity:      str,
    case:          str,
    score:         str,
    advice:        str,
    recommendation: str,
) -> str:
    """
    Build and save a PDF report.

    Returns:
        Absolute path to the generated PDF.

    Raises:
        Exception: propagated to caller so the GUI can show an error dialog.
    """
    file_name = _safe_filename(patient_name)
    # Save next to the running script / executable
    output_dir = os.path.abspath(".")
    file_path  = os.path.join(output_dir, file_name)

    doc    = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm,   bottomMargin=2*cm,
    )
    styles  = _build_styles()
    content = []

    # ── Header ────────────────────────────────────────────────────────────────
    content.append(Paragraph("Medical Diagnosis Report", styles["title"]))
    content.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2E86C1")))
    content.append(Spacer(1, 0.3*cm))

    # ── Meta info ─────────────────────────────────────────────────────────────
    content.append(Paragraph("Report Information", styles["section"]))
    now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    for label, value in [("Date & Time", now), ("Patient Name", patient_name)]:
        content.append(Paragraph(f"<b>{label}:</b>", styles["body"]))
        content.append(Paragraph(str(value), styles["value"]))

    content.append(Spacer(1, 0.2*cm))

    # ── Diagnosis ─────────────────────────────────────────────────────────────
    content.append(Paragraph("Diagnosis", styles["section"]))
    for label, value in [
        ("Disease (English)", disease),
        ("Disease (Arabic)",  arabic_disease),
        ("Prediction Confidence", f"{probability:.1f}%"),
    ]:
        content.append(Paragraph(f"<b>{label}:</b>", styles["body"]))
        content.append(Paragraph(str(value), styles["value"]))

    content.append(Spacer(1, 0.2*cm))

    # ── Risk assessment ───────────────────────────────────────────────────────
    content.append(Paragraph("Risk Assessment", styles["section"]))
    for label, value in [
        ("Risk Level",          risk),
        ("Severity Level",      severity),
        ("Case Classification", case),
        ("Risk Score",          score),
    ]:
        content.append(Paragraph(f"<b>{label}:</b>", styles["body"]))
        content.append(Paragraph(str(value), styles["value"]))

    content.append(Spacer(1, 0.2*cm))

    # ── Medical advice ────────────────────────────────────────────────────────
    content.append(Paragraph("Medical Guidance", styles["section"]))
    for label, value in [
        ("Medical Advice",       advice),
        ("System Recommendation", recommendation),
    ]:
        content.append(Paragraph(f"<b>{label}:</b>", styles["body"]))
        content.append(Paragraph(str(value), styles["value"]))

    content.append(Spacer(1, 0.5*cm))
    content.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0")))
    content.append(Spacer(1, 0.2*cm))
    content.append(Paragraph(
        "<i>This report is generated by an AI-assisted system. "
        "It is not a substitute for professional medical advice.</i>",
        styles["body"]
    ))

    # ── Build ─────────────────────────────────────────────────────────────────
    doc.build(content)
    logger.info("PDF report written to: %s", file_path)
    return file_path
