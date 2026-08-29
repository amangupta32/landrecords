/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        gov: {
          blue: '#0F2C59',
          gold: '#D8A25E',
          accent: '#1E40AF',
          light: '#F8FAFC',
          dark: '#0B132B'
        }
      }
    },
  },
  plugins: [],
}
