/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary-text': '#1F2937',
        'accent': '#6366F1',
        'background': '#F9FAFB',
        'card': '#FFFFFF',
        'warning': '#FBBF24',
        'success': '#10B981',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'Roboto', 'Helvetica Neue', 'sans-serif'],
      }
    },
  },
  plugins: [],
} 