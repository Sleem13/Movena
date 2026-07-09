/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        clinical: {
          ink: "#14213d",
          teal: "#0f766e",
          mint: "#dff7ef",
          line: "#d7e1ea",
          panel: "#f7fafc",
        },
      },
      boxShadow: {
        panel: "0 12px 30px rgba(15, 23, 42, 0.08)",
      },
    },
  },
  plugins: [],
};
