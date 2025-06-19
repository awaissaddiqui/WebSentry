/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#00f5ff', // lighter cyan
          DEFAULT: '#00d1ff', // logo cyan
          dark: '#4b0082' // deep violet/indigo
        },
        secondary: {
          light: '#b388ff', // lavender glow
          DEFAULT: '#6a00f4', // cyber purple
          dark: '#4b0082'
        },
        background: {
          DEFAULT: '#0b0f1a', // main app background
          surface: '#111927', // card/surface background
        },
        text: {
          primary: '#ffffff',
          secondary: '#b0b9c6',
          muted: '#6c7a89'
        },
        success: '#52c41a',
        warning: '#faad14',
        danger: '#f5222d',
      },
      boxShadow: {
        card: '0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)',
        'card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
      },
      backgroundImage: {
        'primary-gradient': 'linear-gradient(to right, #00f5ff, #4b0082)',
      }
    },
  },
  plugins: [],
}
