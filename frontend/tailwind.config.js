/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: '#FAF7F2',
        surface: {
          DEFAULT: '#FFFFFF',
          hover: '#F9F6F1',
        },
        text: {
          DEFAULT: '#1F1D20',
          secondary: '#4A4745',
          muted: '#6F6B65',
          inverse: '#FFFFFF',
        },
        border: {
          DEFAULT: '#E9E4DE',
          hover: '#D9D3CC',
          focus: '#E46E58',
        },
        accent: {
          50: '#FEF6F4',
          100: '#FDEAE5',
          200: '#FBD5CC',
          300: '#F7B5A5',
          400: '#F28E76',
          500: '#E46E58',
          600: '#D55843',
          700: '#CC5B46',
          800: '#A84A39',
          900: '#8A3F30',
        },
        neutral: {
          50: '#FAF9F8',
          100: '#F5F3F0',
          200: '#E9E4DE',
          300: '#D9D3CC',
          400: '#B8B1A8',
          500: '#8F8780',
          600: '#6F6B65',
          700: '#4A4745',
          800: '#2E2C2A',
          900: '#1F1D20',
        },
        success: {
          DEFAULT: '#2F7D57',
          bg: '#E8F5EE',
        },
        warning: {
          DEFAULT: '#B16A2E',
          bg: '#FDF4E8',
        },
        info: {
          DEFAULT: '#4F6D9A',
          bg: '#EBF0F7',
        },
        error: {
          DEFAULT: '#C94A3D',
          bg: '#FDEEED',
        },
      },
      fontFamily: {
        serif: ['Lora', 'Georgia', 'Times New Roman', 'serif'],
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'SF Pro Text', 'Segoe UI', 'system-ui', 'sans-serif'],
      },
      spacing: {
        '1': '8px',
        '2': '16px',
        '3': '24px',
        '4': '32px',
        '5': '40px',
        '6': '48px',
        '8': '64px',
        '10': '80px',
        '12': '96px',
      },
      borderRadius: {
        'sm': '8px',
        'md': '12px',
        'lg': '16px',
        'xl': '24px',
        'pill': '9999px',
      },
      boxShadow: {
        'xs': '0 1px 2px rgba(31, 29, 32, 0.04)',
        'sm': '0 2px 4px rgba(31, 29, 32, 0.06), 0 1px 2px rgba(31, 29, 32, 0.04)',
        'md': '0 4px 8px rgba(31, 29, 32, 0.08), 0 2px 4px rgba(31, 29, 32, 0.04)',
        'lg': '0 8px 16px rgba(31, 29, 32, 0.10), 0 4px 8px rgba(31, 29, 32, 0.06)',
      },
      transitionDuration: {
        '120': '120ms',
        '150': '150ms',
        '160': '160ms',
      },
      transitionTimingFunction: {
        'ease-out': 'cubic-bezier(0, 0, 0.2, 1)',
      },
    },
  },
  plugins: [],
}
