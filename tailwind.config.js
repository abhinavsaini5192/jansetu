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
        navy: {
          950: '#070C18',
          900: '#0B132B',
          850: '#111C3A',
          800: '#1C2541',
          750: '#233054',
          700: '#2D3E6B',
          600: '#3A506B',
          500: '#516E94',
        },
        jharkhand: {
          green: '#138808',
          saffron: '#FF9933',
          blue: '#0F4C81',
          gold: '#EAB308',
        },
        brand: {
          primary: '#3B82F6',
          secondary: '#6366F1',
          teal: '#14B8A6',
          emerald: '#10B981',
          amber: '#F59E0B',
          rose: '#F43F5E',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'glow-sm': '0 0 15px rgba(59, 130, 246, 0.15)',
        'glow-md': '0 0 25px rgba(59, 130, 246, 0.25)',
        'glow-teal': '0 0 25px rgba(20, 184, 166, 0.25)',
        'glow-emerald': '0 0 25px rgba(16, 185, 129, 0.25)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 4s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-6px)' },
        }
      }
    },
  },
  plugins: [],
}
