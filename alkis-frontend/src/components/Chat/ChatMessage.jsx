import React from 'react';

// single message bubble (user blue, bot grey) 

const ChatMessage = ({ message }) => {
    const isUser = message.role === 'user';

    // Simple function to render bold text
    const renderContent = (text) => {
        const parts = text.split(/(\*\*.*?\*\*)/g);
        return parts.map((part, index) => {
            if (part.startsWith('**') && part.endsWith('**')) {
                return <strong key={index}>{part.slice(2, -2)}</strong>;
            }
            return part;
        });
    };

    return (
        <span
            className={`rounded-lg p-3 text-sm ${isUser ? 'bg-blue-600' : 'bg-gray-800'
                }`}
            style={{ display: "block" }}
        >
            {renderContent(message.content)}
        </span>
    );
};

export default ChatMessage;