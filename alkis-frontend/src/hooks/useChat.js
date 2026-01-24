import { useState, useEffect } from 'react';
import { chatAPI } from '../services/api';
// import websocketService from '../services/websocket';

// manages chat messages, loading state and sending messages

const parseBuildings = (results) => {
    return results.map((item, index) => {
        // item is an array with one object containing 'gebäudegemoetrie'
        const gebaeude = Array.isArray(item) ? item[0] : item;

        const firstKey = Object.keys(item)[0];
        const geoJsonString = gebaeude[firstKey];

        try {
            const geoJson = JSON.parse(geoJsonString);

            return {
                id: index, // or use a unique ID if available
                name: gebaeude.name || 'Building', // adjust based on actual data
                geometry: geoJson,
                area: gebaeude.area || 0,
                floors: gebaeude.floors || 0,
                district: gebaeude.district || ''
            };
        } catch (error) {
            console.error('Error parsing GeoJSON:', error);
            return null;
        }
    }).filter(b => b !== null);
};

export const useChat = () => {
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: 'Welcome to AX_Ploration. Ask questions about ALKIS building data in Berlin.'
        }
    ]);
    const [isLoading, setIsLoading] = useState(false);
    const [buildings, setBuildings] = useState([]);

    const sendMessage = async (content) => {
        // Add user message
        const userMessage = { role: 'user', content };
        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);

        try {
            // Mock response until backend is ready
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 1000));

            /* Mock response based on query
            let mockResponse = "I understand you're asking about ALKIS building data. Your backend will process this query once connected.";

            if (content.toLowerCase().includes('university')) {
                mockResponse = "Found 8 university buildings with area ≥ 2,000 m². Once your backend is connected, I'll show you real results from the Neo4j database.";
            } else if (content.toLowerCase().includes('school')) {
                mockResponse = "Searching for school buildings in the ALKIS database...";
            } else if (content.toLowerCase().includes('area')) {
                mockResponse = "I can help you filter buildings by area. Please specify the criteria.";
            }

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: mockResponse
            }]);
            */

            //uncomment when backend connected:


            // const response = await chatAPI.sendMessage(content);
            const { final_answer: final_answer, results: results } = await chatAPI.sendMessage(content);
            console.log("final_answer", final_answer);
            console.log("results", results);

            const processedBuildings = parseBuildings(results);
            console.log("processedBuildings", processedBuildings);
            setBuildings(processedBuildings);



            if (final_answer) {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: final_answer
                }]);
            }


        } catch (error) {
            console.error('Error sending message:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please make sure the backend is running and try again.'
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return {
        messages,
        isLoading,
        sendMessage,
        buildings,
    };
};
