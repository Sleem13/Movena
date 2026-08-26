/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        clinical: {
          ink: "rgb(var(--color-ink) / <alpha-value>)",
          navy: "rgb(var(--color-ink) / <alpha-value>)",
          blue: "rgb(var(--color-blue) / <alpha-value>)",
          sky: "rgb(var(--color-sky) / <alpha-value>)",
          teal: "rgb(var(--color-teal) / <alpha-value>)",
          mint: "rgb(var(--color-mint) / <alpha-value>)",
          line: "rgb(var(--color-line) / <alpha-value>)",
          panel: "rgb(var(--color-panel) / <alpha-value>)",
        },
      },
      borderRadius: {
        "3xl": "1.5rem",
      },
      boxShadow: {
        panel: "0 10px 30px rgba(7, 27, 74, 0.055)",
        lift: "0 24px 64px rgba(7, 27, 74, 0.13)",
        soft: "0 2px 10px rgba(7, 27, 74, 0.06)",
      },
    },
  },
  plugins: [],
};
