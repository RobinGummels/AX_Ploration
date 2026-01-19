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
        const healthCheckAPI = await api.get('/');
        // console.log(healthCheckAPI);
        const healthCheckDB = await api.get('/health');
        if (healthCheckAPI.data.status == "online") {
            if (healthCheckDB.data.status == "healthy") {
                const response = (await api.post('/query', { query: message, stream: false })); //stream=T or F for results
                //return (response.data.final_answer, response.data.results);
                return {
                    final_answer: response.data.final_answer,
                    results: response.data.results,
                };
            }
            else console.log("Databse not connected.")
        }
        else console.log("API not connected.")
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