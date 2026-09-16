"""PDF experiment and FDA-style safety report generation (ReportLab)."""

from __future__ import annotations

from io import BytesIO
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .lab import lab


NAVY = colors.HexColor("#042f4a")
CYAN = colors.HexColor("#22d3ee")
INK = colors.HexColor("#e2e8f0")
BG = colors.HexColor("#0b1220")


def _styles():
    base = getSampleStyleSheet()
    title = ParagraphStyle(
        "TwinTitle",
        parent=base["Title"],
        textColor=NAVY,
        fontSize=18,
        spaceAfter=8,
    )
    body = ParagraphStyle(
        "TwinBody",
        parent=base["BodyText"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
    )
    h = ParagraphStyle(
        "TwinH",
        parent=base["Heading2"],
        textColor=NAVY,
        fontSize=13,
        spaceBefore=10,
        spaceAfter=6,
    )
    return title, body, h


def build_experiment_pdf() -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, title="OrganTwin AI Experiment Report")
    title, body, h = _styles()
    live = lab.live()
    story = [
        Paragraph("OrganTwin AI — Organ-on-Chip Experiment Report", title),
        Paragraph(datetime.now(timezone.utc).strftime("Generated %Y-%m-%d %H:%M UTC"), body),
        Spacer(1, 8),
        Paragraph("Study objective", h),
        Paragraph(
            "This digital twin assay estimates acute drug toxicity on liver, heart, and kidney chips "
            "to de-risk compounds before animal studies. Sensor traces are simulated perfusion readouts; "
            "toxicity labels come from a Random Forest trained on synthetic OoC physiology.",
            body,
        ),
    ]
    rows = [["Organ", "Drug", "Dose (mg)", "Health", "AI call", "Risk", "Survival %"]]
    for organ in live.organs:
        pred = live.predictions.get(organ.organ)
        rows.append(
            [
                organ.organ,
                organ.drug,
                f"{organ.dose_mg:.1f}",
                f"{organ.health_score:.1f}",
                pred.label if pred else "—",
                pred.risk_level if pred else "—",
                f"{organ.survival_rate:.1f}",
            ]
        )
    table = Table(rows, colWidths=[0.9 * inch, 1.1 * inch, 1.0 * inch, 0.8 * inch, 1.4 * inch, 0.8 * inch, 1.0 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#94a3b8")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story += [Paragraph("Live chip panel", h), table, Spacer(1, 10)]
    story.append(Paragraph("Sensor history (latest values)", h))
    for organ in live.organs:
        bits = ", ".join(f"{k}={v.value}{v.unit}" for k, v in organ.sensors.items())
        story.append(Paragraph(f"<b>{organ.organ.title()}:</b> {bits}", body))
    story.append(Paragraph("AI recommendations", h))
    for organ, pred in live.predictions.items():
        for line in pred.insights[:4]:
            story.append(Paragraph(f"• [{organ}] {line}", body))
    if live.alerts:
        story.append(Paragraph("Anomaly alerts", h))
        for alert in live.alerts[:8]:
            story.append(Paragraph(f"• ({alert.severity}) {alert.message}", body))
    doc.build(story)
    return buf.getvalue()


def build_fda_style_pdf() -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, title="OrganTwin Simulated FDA Safety Package")
    title, body, h = _styles()
    live = lab.live()
    ranking = lab.ranking()
    story = [
        Paragraph("SIMULATED FDA-STYLE SAFETY PACKAGE", title),
        Paragraph("Module 4-inspired nonclinical overview — NOT an official FDA submission.", body),
        Paragraph("Sponsor: OrganTwin AI Digital Twin Laboratory  |  Species: human-relevant organ-on-chip", body),
        Paragraph("Safety pharmacology & acute tox (in silico + OoC)", h),
        Paragraph(
            "ICH S7A/S7B analogue: cardiac contractility and beat-rate; hepatic viability/lactate; "
            "renal filtration and metabolite load. No animal subjects were used.",
            body,
        ),
    ]
    rows = [["Compound", "Toxicity score", "Class", "Interpretation"]]
    for item in ranking:
        rows.append([item["display"], str(item["toxicity_score"]), item["safety_class"], item["note"][:80]])
    table = Table(rows, colWidths=[1.6 * inch, 1.1 * inch, 1.0 * inch, 3.5 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story += [table, Paragraph("NOAEL / safety margin (simulated)", h)]
    story.append(
        Paragraph(
            "Drug A: NOAEL supported across 36 h perfusion. Drug B: LOAEL near 20 mg with reversible stress. "
            "Drug C: no NOAEL identified — severe cytotoxicity and predicted organ failure. "
            "Recommended path: Drug A IND-enabling in vitro package; Drug C hold.",
            body,
        )
    )
    story.append(Paragraph("Benefit vs animal testing", h))
    story.append(
        Paragraph(
            "This twin panel can screen acute tox in hours rather than weeks of rodent LD50 work, "
            "reducing sentinel animal use while preserving a decision-quality risk call for pharma R&amp;D.",
            body,
        )
    )
    for organ in live.organs:
        pred = live.predictions.get(organ.organ)
        story.append(
            Paragraph(
                f"{organ.organ.title()}: health {organ.health_score}, AI {pred.label if pred else 'n/a'}, "
                f"damage {organ.damage_percent}%.",
                body,
            )
        )
    doc.build(story)
    return buf.getvalue()
