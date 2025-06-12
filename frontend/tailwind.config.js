/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Stripe's color palette
        primary: {
          50: '#f6f8fa',
          100: '#edf1f7',
          200: '#e5e9f0',
          300: '#d1d9e6',
          400: '#a3b1c6',
          500: '#7a8ba6',
          600: '#556783',
          700: '#364761',
          800: '#1a2c42',
          900: '#0a1628',
        },
        accent: {
          // Stripe's purple
          DEFAULT: '#635bff',
          light: '#7a73ff',
          dark: '#4b44ff',
        },
        success: {
          DEFAULT: '#24b47e',
          light: '#3ecf8e',
          dark: '#1a9c6e',
        },
        warning: {
          DEFAULT: '#f7b84b',
          light: '#f8c46c',
          dark: '#f6ac2a',
        },
        error: {
          DEFAULT: '#cd3d64',
          light: '#d65c7f',
          dark: '#c41e49',
        },
      },
      // Stripe-like shadows
      boxShadow: {
        'stripe-sm': '0 2px 5px -1px rgba(50,50,93,.25), 0 1px 3px -1px rgba(0,0,0,.3)',
        'stripe-md': '0 6px 12px -2px rgba(50,50,93,.25), 0 3px 7px -3px rgba(0,0,0,.3)',
        'stripe-lg': '0 13px 27px -5px rgba(50,50,93,.25), 0 8px 16px -8px rgba(0,0,0,.3)',
      },
    },
  },
  plugins: [],
} 