"""Rule-based real-time alerts for sudden physiological collapse."""

from __future__ import annotations

from .organ_sim import OrganChip


def detect_anomalies(chip: OrganChip) -> list[dict]:
    alerts: list[dict] = []
    s, p = chip.state, chip.previous
    organ = chip.organ

    if "oxygen" in s and "oxygen" in p:
        drop = p["oxygen"] - s["oxygen"]
        if drop >= 0.55:
            alerts.append(
                {
                    "kind": "oxygen_drop",
                    "severity": "critical" if drop >= 1.0 else "warning",
                    "message": f"{organ.title()} hypoxia event: O₂ fell {drop:.1f}% in one tick.",
                }
            )
        elif s["oxygen"] < 78:
            alerts.append(
                {
                    "kind": "oxygen_drop",
                    "severity": "warning",
                    "message": f"{organ.title()} oxygen below perfusion safety floor ({s['oxygen']:.1f}%).",
                }
            )

    if "ph" in s:
        if s["ph"] < 7.20 or s["ph"] > 7.55:
            alerts.append(
                {
                    "kind": "ph_shift",
                    "severity": "critical" if s["ph"] < 7.05 else "warning",
                    "message": f"{organ.title()} pH excursion to {s['ph']:.2f} (target 7.35–7.45).",
                }
            )
        elif "ph" in p and abs(s["ph"] - p["ph"]) >= 0.0075:
            alerts.append(
                {
                    "kind": "ph_shift",
                    "severity": "warning",
                    "message": f"{organ.title()} rapid pH delta {s['ph'] - p['ph']:+.3f}.",
                }
            )

    if "viability" in s:
        drop_v = p.get("viability", s["viability"]) - s["viability"]
        if drop_v >= 0.45 or s["viability"] < 70:
            alerts.append(
                {
                    "kind": "cell_death",
                    "severity": "critical" if s["viability"] < 55 else "warning",
                    "message": f"{organ.title()} cell-death event — viability {s['viability']:.1f}%.",
                }
            )

    return [
        {
            "organ": organ,
            **item,
        }
        for item in alerts
    ]
