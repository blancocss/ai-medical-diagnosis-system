from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime


def generate_medical_report(

        patient_name,
        disease,
        arabic_disease,
        probability,
        risk,
        severity,
        case,
        score,
        advice,
        recommendation

):

    # اسم الملف

    file_name = f"Medical_Report_{patient_name}.pdf"

    # إنشاء الملف

    document = SimpleDocTemplate(
        file_name
    )

    styles = getSampleStyleSheet()

    content = []

    # Title

    title = Paragraph(
        "Medical Diagnosis Report",
        styles["Title"]
    )

    content.append(title)

    content.append(
        Spacer(1, 20)
    )

    # Date

    date_text = Paragraph(
        f"Date: {datetime.now()}",
        styles["Normal"]
    )

    content.append(date_text)

    content.append(
        Spacer(1, 15)
    )

    # Patient

    patient = Paragraph(
        f"Patient Name: {patient_name}",
        styles["Normal"]
    )

    content.append(patient)

    content.append(
        Spacer(1, 15)
    )

    # Disease

    disease_text = Paragraph(
        f"Disease: {disease}",
        styles["Normal"]
    )

    content.append(disease_text)

    content.append(
        Spacer(1, 15)
    )

    # Probability

    probability_text = Paragraph(
        f"Probability: {probability:.2f} %",
        styles["Normal"]
    )

    content.append(probability_text)

    content.append(
        Spacer(1, 15)
    )

    # Risk

    risk_text = Paragraph(
        f"Risk Level: {risk}",
        styles["Normal"]
    )

    content.append(risk_text)

    content.append(
        Spacer(1, 15)
    )

    # Severity

    severity_text = Paragraph(
        f"Severity Level: {severity}",
        styles["Normal"]
    )

    content.append(severity_text)

    content.append(
        Spacer(1, 15)
    )

    # Case

    case_text = Paragraph(
        f"Case Classification: {case}",
        styles["Normal"]
    )

    content.append(case_text)

    content.append(
        Spacer(1, 15)
    )

    # Score

    score_text = Paragraph(
        f"Risk Score: {score}",
        styles["Normal"]
    )

    content.append(score_text)

    content.append(
        Spacer(1, 20)
    )

    # Advice

    advice_text = Paragraph(
        f"Medical Advice: {advice}",
        styles["Normal"]
    )

    content.append(advice_text)

    content.append(
        Spacer(1, 20)
    )

    # Recommendation

    recommendation_text = Paragraph(
        f"System Recommendation: {recommendation}",
        styles["Normal"]
    )

    content.append(
        recommendation_text
    )

    # Build PDF

    document.build(
        content
    )

    return file_name