"use client";

import { useEffect, useState } from "react";
import { getJson, LiveState } from "@/lib/api";

export function useLive(intervalMs = 2500) {
  const [data, setData] = useState<LiveState | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    const load = async () => {
      try {
        const next = await getJson<LiveState>("/api/live");
        if (alive) {
          setData(next);
          setError(null);
        }
      } catch (err) {
        if (alive) setError(err instanceof Error ? err.message : "API unreachable");
      }
    };
    load();
    const id = setInterval(load, intervalMs);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, [intervalMs]);

  return { data, error };
}
