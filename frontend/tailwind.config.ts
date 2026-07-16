import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        priority: {
          red: "#dc2626",
          yellow: "#d97706",
          green: "#16a34a",
        },
      },
    },
  },
  plugins: [],
};

export default config;
