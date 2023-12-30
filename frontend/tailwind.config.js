/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      keyframes: {

      },
      animation: {
        
      },
      fontFamily: {
        poppins: ['Poppins','sans-serif'],
      },
    },
  },
  daisyui: {
    themes: [
      {
        mm_dark: {
          "primary": "#E38942",
          
          "secondary": "#e11d48",
                   
          "accent": "#6d28d9",
                   
          "neutral": "#0A1E36",
                   
          "base-100": "#0A1E36",
                   
          "info": "#0284c7",
                   
          "success": "#16a34a",
                   
          "warning": "#facc15",
                   
          "error": "#dc2626",
        },
      }
    ]
  },
  plugins: [require("daisyui")],
}

