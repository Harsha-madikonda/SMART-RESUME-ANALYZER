from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def create_report(result, recommendations, rating):

    pdf = SimpleDocTemplate("ATS_Report.pdf")

    styles = getSampleStyleSheet()

    content = []

    # Title
    content.append(
        Paragraph(
            "SMART RESUME ANALYZER REPORT",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 12))

    # Scores

    content.append(
        Paragraph(
            f"Semantic Match Score: {result['semantic_score']:.2f}%",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Skill Match Score: {result['skill_score']:.2f}%",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Overall Rating: {rating}",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 12))

    # Strengths

    content.append(
        Paragraph(
            "Strengths",
            styles["Heading2"]
        )
    )

    for skill in result["strengths"]:
        content.append(
            Paragraph(
                f"✓ {skill}",
                styles["Normal"]
            )
        )

    content.append(Spacer(1, 12))

    # Missing Skills

    content.append(
        Paragraph(
            "Missing Skills",
            styles["Heading2"]
        )
    )

    for skill in result["missing_skills"]:
        content.append(
            Paragraph(
                f"✗ {skill}",
                styles["Normal"]
            )
        )

    content.append(Spacer(1, 12))

    # Recommendations

    content.append(
        Paragraph(
            "Recommendations",
            styles["Heading2"]
        )
    )

    for recommendation in recommendations:
        content.append(
            Paragraph(
                f"• {recommendation}",
                styles["Normal"]
            )
        )

    pdf.build(content)

    return "ATS_Report.pdf"