export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

// configuration constants (API URLs, map center coordinates, building type codes)

export const MAP_CONFIG = {
    center: [52.52, 13.405], // Berlin coordinates
    zoom: 12,
    minZoom: 10,
    maxZoom: 18
};

export const BUILDING_TYPES = {
    2100: 'University',
    2200: 'School',
    2300: 'Research',
    // Add more ALKIS codes
};