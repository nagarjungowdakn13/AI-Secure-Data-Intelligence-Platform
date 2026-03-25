/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#08111f",
        glow: "#b8f4d1",
        ember: "#ff8f70",
        ocean: "#72d6ff"
      },
      boxShadow: {
        panel: "0 25px 50px rgba(8, 17, 31, 0.35)"
      }
    }
  },
  plugins: []
};
