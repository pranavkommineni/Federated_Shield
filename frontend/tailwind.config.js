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
        background: '#070b14',
        surface: '#0e1526',
        'surface-elevated': '#162038',
        card: '#121a2e',
        cyan: {
          400: '#22d3ee',
          500: '#00f2fe',
          600: '#0891b2',
        },
        purple: {
          400: '#c084fc',
          500: '#a855f7',
          600: '#9333ea',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        glow: '0 0 20px rgba(0, 242, 254, 0.25)',
        'glow-purple': '0 0 20px rgba(168, 85, 247, 0.25)',
      }
    },
  },
  plugins: [],
}
