/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#0f0f0f",
        card: "#1a1a1a",
        border: "#2a2a2a",
        accent: "#2563eb",
      },
    },
  },
  plugins: [],
};
