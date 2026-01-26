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
    sendMessage: async (message, stream, onThinkingMessage) => {
        const healthCheckAPI = await api.get('/');
        // console.log(healthCheckAPI);
        const healthCheckDB = await api.get('/health');
        if (healthCheckAPI.data.status == "online") {
            if (healthCheckDB.data.status == "healthy") {

                if (stream === false) {
                    const response = (await api.post('/query', { query: message, stream: stream })); //stream=T or F for results
                    console.log("API response:", response.data);
                    //return (response.data.final_answer, response.data.results);
                    return {
                        final_answer: response.data.final_answer,
                        results: response.data.results,
                    };
                }
                else {
                    const response = await fetch(`${API_BASE_URL}/query`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ query: message, stream: stream }),
                    });

                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let finalAnswer = null;
                    let results = null;

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;

                        const chunk = decoder.decode(value);
                        const lines = chunk.split('\n');

                        for (const line of lines) {
                            if (line.startsWith('data: ')) {
                                const jsonData = line.slice(6); // Remove 'data: ' prefix
                                try {
                                    const parsed = JSON.parse(jsonData);

                                    if (parsed.type === 'message') {
                                        console.log('Streaming message:', parsed.content);
                                        if (onThinkingMessage) {
                                            onThinkingMessage(parsed.content);
                                        }
                                    } else if (parsed.type === 'final') {
                                        console.log('Final state:', parsed.state);
                                        console.log('Final answer:', parsed.state.final_answer);
                                        finalAnswer = parsed.state.final_answer;
                                        results = parsed.state.results;
                                    } else if (parsed.type === 'error') {
                                        console.error('Error:', parsed.error);
                                    }
                                } catch (e) {
                                    // Ignore parsing errors for incomplete chunks
                                }
                            }
                        }

                    }

                    return {
                        final_answer: finalAnswer,
                        results: results,
                    };
                }
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