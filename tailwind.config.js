/** @type {import('tailwindcss').Config} */

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        background: "#0f172a", // Midnight blue
        foreground: "#f8fafc",
        border: "rgba(255, 255, 255, 0.1)",
        input: "rgba(255, 255, 255, 0.1)",
        ring: "#8b5cf6",
        primary: {
          DEFAULT: "#8b5cf6", // Electric purple
          foreground: "#ffffff",
          hover: "#7c3aed",
        },
        secondary: {
          DEFAULT: "#14b8a6", // Teal
          foreground: "#ffffff",
          hover: "#0d9488",
        },
        card: {
          DEFAULT: "rgba(30, 41, 59, 0.7)", // Glassmorphism base
          foreground: "#f8fafc",
          border: "rgba(255, 255, 255, 0.1)",
        },
        accent: {
          DEFAULT: "#f59e0b",
          foreground: "#ffffff",
        },
        muted: {
          DEFAULT: "#334155",
          foreground: "#94a3b8",
        },
      },
      backgroundImage: {
        'glass-gradient': 'linear-gradient(to bottom right, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.8))',
        'primary-gradient': 'linear-gradient(to right, #8b5cf6, #14b8a6)',
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        pulse: {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: .5 },
        }
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [],
};