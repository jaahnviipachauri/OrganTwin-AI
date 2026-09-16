export type SensorPoint = { metric: string; value: number; unit: string };

export type OrganSnapshot = {
  organ: string;
  health_score: number;
  stress_level: number;
  survival_rate: number;
  damage_percent: number;
  condition: string;
  sensors: Record<string, SensorPoint>;
  drug: string;
  dose_mg: number;
  duration_h: number;
  exposure_elapsed_h: number;
  failure_eta_min: number | null;
};

export type AlertOut = {
  id?: number;
  organ: string;
  severity: string;
  kind: string;
  message: string;
  created_at?: string;
};

export type ToxicityOut = {
  organ: string;
  label: string;
  confidence: number;
  probabilities: Record<string, number>;
  risk_level: string;
  toxicity_probability: number;
  anomaly_score: number;
  is_anomaly: boolean;
  insights: string[];
};

export type LiveState = {
  ticks: number;
  organs: OrganSnapshot[];
  alerts: AlertOut[];
  predictions: Record<string, ToxicityOut>;
  active_experiments: number;
  toxicity_alerts: number;
  mean_health: number;
};

export type DrugInfo = {
  id: string;
  display: string;
  toxicity: number;
  class: string;
  note: string;
};

export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API ${path} failed (${res.status})`);
  return res.json();
}

export async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
