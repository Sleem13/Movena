/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        clinical: {
          ink: "#10243e",
          navy: "#173b63",
          blue: "#2563eb",
          teal: "#0f8f83",
          mint: "#e8f8f4",
          line: "#dce6ee",
          panel: "#f7fafc",
        },
      },
      boxShadow: {
        panel: "0 12px 32px rgba(31, 62, 89, 0.08)",
        lift: "0 20px 50px rgba(31, 62, 89, 0.12)",
      },
    },
  },
  plugins: [],
};
