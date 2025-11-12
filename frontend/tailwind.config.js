/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'inter': ['Inter', 'sans-serif'],
      },
      colors: {
        'purple-gradient-start': '#6B7FE8',
        'purple-gradient-end': '#5B6FD8',
      },
      backgroundImage: {
        'purple-gradient': 'linear-gradient(135deg, #6B7FE8 0%, #5B6FD8 100%)',
      },
      boxShadow: {
        'card': '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
      }
    },
  },
  plugins: [],
}