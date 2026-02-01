import React from 'react';

// single message bubble (user blue, bot grey) 

const ChatMessage = ({ message }) => {
    const isUser = message.role === 'user';

    // Function to render text with bold formatting and line breaks
    const renderContent = (text) => {
        // Split by line breaks first
        const lines = text.split('\n');
        
        return lines.map((line, lineIndex) => {
            // Process bold text (**text**)
            const parts = line.split(/(\*\*.*?\*\*)/g);
            const processedLine = parts.map((part, partIndex) => {
                if (part.startsWith('**') && part.endsWith('**')) {
                    return <strong key={partIndex}>{part.slice(2, -2)}</strong>;
                }
                return part;
            });
            
            // Add line break after each line except the last
            return (
                <React.Fragment key={lineIndex}>
                    {processedLine}
                    {lineIndex < lines.length - 1 && <br />}
                </React.Fragment>
            );
        });
    };

    return (
        <span
            className={`rounded-lg p-3 text-sm ${isUser ? 'bg-blue-600' : 'bg-gray-800'
                }`}
            style={{ display: "block", whiteSpace: "pre-wrap" }}
        >
            {renderContent(message.content)}
        </span>
    );
};

export default ChatMessage;