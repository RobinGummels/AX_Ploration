import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/global.css'
import 'leaflet/dist/leaflet.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// run in cd alkis-frontend
// use npm run dev
// this uses npm install -D tailwindcss@^3.4.0 postcss autoprefixer