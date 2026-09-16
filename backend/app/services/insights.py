"""Narrative research insights generated from live twin + model outputs."""

from __future__ import annotations

from .organ_sim import DRUGS, OrganChip


def build_insights(chip: OrganChip, prediction: dict) -> list[str]:
    twin = chip.twin_metrics()
    drug_meta = DRUGS.get(chip.drug, {})
    insights = [
        f"{chip.organ.title()}-on-chip is {twin['condition'].lower()} with health {twin['health_score']}/100.",
        f"Model call: {prediction['label']} (confidence {prediction['confidence']*100:.1f}%, risk {prediction['risk_level']}).",
    ]
    if chip.drug != "None":
        insights.append(
            f"{drug_meta.get('display', chip.drug)} at {chip.dose_mg:.1f} mg for {chip.duration_h:.1f} h. {drug_meta.get('note', '')}"
        )
    if twin["failure_eta_min"]:
        insights.append(
            f"Early-warning: organ failure trajectory detected. Estimated time-to-critical ≈ {twin['failure_eta_min']} min at current slope."
        )
    if prediction.get("is_anomaly"):
        insights.append("Isolation Forest flagged this sensor vector as out-of-distribution versus healthy training chips.")
    if chip.organ == "liver" and chip.state.get("lactate", 0) > 3:
        insights.append("Hepatic lactate dump suggests glycolytic shift — consider reducing dose or shortening perfusion.")
    if chip.organ == "heart" and chip.state.get("contractility", 100) < 60:
        insights.append("Inotropic collapse on-chip: contractility is below the 60% rescue threshold used in cardiac OoC assays.")
    if chip.organ == "kidney" and chip.state.get("toxic_metabolites", 0) > 10:
        insights.append("Nephrotoxic metabolite accumulation is outpacing filtration. Barrier leak likely.")
    insights.append(
        "Recommendation: prioritize human-relevant OoC + in-silico twins before any in-vivo escalation; this panel replaces sentinel animal cohorts for acute tox."
    )
    return insights
