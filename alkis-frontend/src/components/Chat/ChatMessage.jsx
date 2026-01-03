import React from 'react';

// single message bubble (user blue, bot grey) 

const ChatMessage = ({ message }) => {
    const isUser = message.role === 'user';

    return (
        <div
            className={`rounded-lg p-3 text-sm ${isUser ? 'bg-blue-600' : 'bg-gray-800'
                }`}
        >
            {message.content}
        </div>
    );
};

export default ChatMessage;