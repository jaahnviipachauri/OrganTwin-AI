import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        lab: {
          bg: "#020617",
          panel: "#071525",
          cyan: "#22d3ee",
          blue: "#38bdf8",
          danger: "#fb7185",
          ok: "#34d399",
        },
      },
      boxShadow: {
        glow: "0 0 40px rgba(34, 211, 238, 0.18)",
      },
      backgroundImage: {
        grid: "linear-gradient(rgba(34,211,238,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(34,211,238,0.06) 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};

export default config;
