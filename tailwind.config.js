/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.{html, jinja}"],
  theme: {
    extend: {
        fontFamily: {
           'Rising Sun': ['RisingSun', 'sans'], 
           'IBM Plex': ['IBMPlex', 'sans'],
        },
        colors: {
            'darkBlue': '#1E1E31',
            'darkPink': '#FF6AF2',
            'lightBlue': '#4082F5',
        }
    }
  },
  plugins: []
}

