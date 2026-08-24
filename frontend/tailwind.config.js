/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        clinical: {
          ink: "#071b4a",
          navy: "#071b4a",
          blue: "#0b5ed7",
          sky: "#eaf3ff",
          teal: "#0f8f83",
          mint: "#e8f8f4",
          line: "#dce3ee",
          panel: "#f8fafc",
        },
      },
      borderRadius: {
        "3xl": "1.5rem",
      },
      boxShadow: {
        panel: "0 10px 30px rgba(31, 62, 89, 0.07)",
        lift: "0 24px 64px rgba(31, 62, 89, 0.14)",
        soft: "0 2px 10px rgba(31, 62, 89, 0.06)",
      },
    },
  },
  plugins: [],
};
