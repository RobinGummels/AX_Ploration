import axios from 'axios';
import { API_BASE_URL } from '../utils/constants';

// axios instance and api functions for chat, buildings, statistics, map data (needs to be connected to backend)

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const chatAPI = {
    sendMessage: async (message) => {
        const response = await api.post('/chat', { message });
        return response.data;
    },
};

export const buildingsAPI = {
    search: async (query) => {
        const response = await api.get('/buildings/search', { params: query });
        return response.data;
    },

    getById: async (id) => {
        const response = await api.get(`/buildings/${id}`);
        return response.data;
    },

    getStatistics: async (filters) => {
        const response = await api.get('/buildings/statistics', { params: filters });
        return response.data;
    },
};

export const mapAPI = {
    getGeometry: async (buildingIds) => {
        const response = await api.post('/map/geometry', { buildingIds });
        return response.data;
    },
};

export default api;