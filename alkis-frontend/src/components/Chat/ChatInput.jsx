import React, { useState } from 'react';
import { Search } from 'lucide-react';

// text input field, send button at bottom of chat window

const ChatInput = ({ onSend, disabled, showThinking, onToggleThinking }) => {
    const [value, setValue] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (value.trim() && !disabled) {
            onSend(value);
            setValue('');
        }
    };

    return (
        <form onSubmit={handleSubmit} className="flex gap-2">
            <div className="flex items-center gap-2">
                <input
                    type="checkbox"
                    id="showThinking"
                    checked={showThinking}
                    onChange={(e) => onToggleThinking(e.target.checked)}
                    disabled={disabled}
                    className="w-4 h-4 text-blue-600 bg-gray-800 border-gray-600 rounded focus:ring-blue-600 focus:ring-2 cursor-pointer disabled:opacity-50"
                    title="Show thinking process"
                />
                <label 
                    htmlFor="showThinking" 
                    className="text-xs text-gray-400 cursor-pointer select-none"
                    title="Show thinking process"
                >
                    Show thinking
                </label>
            </div>
            <input
                type="text"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="Ask about buildings..."
                disabled={disabled}
                className="flex-1 bg-gray-800 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 disabled:opacity-50"
            />
            <button
                type="submit"
                disabled={disabled || !value.trim()}
                className="bg-blue-600 p-2 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                <Search className="w-4 h-4" />
            </button>
        </form>
    );
};

export default ChatInput;