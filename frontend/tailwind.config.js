/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Manrope', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand: {
          50: '#f0f9f4',
          100: '#dcf2e5',
          200: '#bce4cd',
          300: '#8bcfab',
          400: '#54b383',
          500: '#319765',
          600: '#22794f',
          700: '#1c6141',
          800: '#194e36',
          900: '#16402e',
        },
        slate: {
          850: '#172033',
          950: '#0f1629',
        },
      },
    },
  },
  plugins: [],
}
