import React, { useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

// for left side, icon and header, chat window
// chat history and input field

const ChatSidebar = ({ messages, onSendMessage, isLoading }) => {
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    return (
        <div className="w-80 bg-gray-900 flex flex-col border-r border-gray-800">
            {/* Header */}
            <div className="p-4 border-b border-gray-800 flex items-center gap-3">
                <img
                    src="/logo.svg"
                    alt="AX Logo"
                    className="w-8 h-8"
                />

                <div>
                    <div className="font-semibold">AX_Ploration</div>
                    <div className="text-xs text-gray-400">Berlin Pilot Region</div>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                <div className="bg-gray-800 rounded-lg p-3">
                    <div className="text-sm font-semibold mb-2">Let's AX_Plore!</div>
                    <div className="text-xs text-gray-400">Buildings are waiting for you...</div>
                </div>

                {messages.map((message, idx) => (
                    <ChatMessage key={idx} message={message} />
                ))}

                {isLoading && (
                    <div className="bg-gray-800 rounded-lg p-3 text-sm">
                        <div className="flex items-center gap-2">
                            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-75" />
                            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-150" />
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-800">
                <ChatInput onSend={onSendMessage} disabled={isLoading} />
            </div>
        </div>
    );
};

export default ChatSidebar;