import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        cream: "#f6f2e9",
        ink: "#152238",
        mint: "#99d98c",
        coral: "#f28482"
      }
    }
  },
  plugins: []
};

export default config;
