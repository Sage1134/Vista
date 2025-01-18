/** @type {import('tailwindcss').Config} */
module.exports = {
  // NOTE: Update this to include the paths to all of your component files.
  content: ["./app/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        transparent: 'transparent',
        current: 'currentColor',
        'white': '#ffffff',
        'midnight': '#121063',
        'blurple': "#6639ff",
      },
      fontFamily: {
        rubik: ['Rubik', 'sans-serif'], 
      },
    },
  },
  plugins: [],
}