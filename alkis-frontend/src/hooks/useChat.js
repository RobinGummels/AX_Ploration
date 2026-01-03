import { useState, useEffect } from 'react';
// import { chatAPI } from '../services/api';
// import websocketService from '../services/websocket';

// manages chat messages, loading state and sending messages

export const useChat = () => {
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: 'Welcome to AX_Ploration. Ask questions about ALKIS building data in Berlin.'
        }
    ]);
    const [isLoading, setIsLoading] = useState(false);

    const sendMessage = async (content) => {
        // Add user message
        const userMessage = { role: 'user', content };
        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);

        try {
            // Mock response until backend is ready
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Mock response based on query
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

            /* uncomment when backend connected:
            import { chatAPI } from '../services/api';
            
            const response = await chatAPI.sendMessage(content);
            
            if (response.message) {
              setMessages(prev => [...prev, { 
                role: 'assistant', 
                content: response.message 
              }]);
            }
            */

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
    };
};
