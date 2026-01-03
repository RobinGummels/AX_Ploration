import React from 'react';
import { AlertCircle, X } from 'lucide-react';

// error display with dismiss button

const ErrorMessage = ({ message, onClose }) => {
    if (!message) return null;

    return (
        <div className="bg-red-900 bg-opacity-50 border border-red-700 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
                <h4 className="text-red-200 font-semibold mb-1">Error</h4>
                <p className="text-red-300 text-sm">{message}</p>
            </div>
            {onClose && (
                <button
                    onClick={onClose}
                    className="text-red-400 hover:text-red-300"
                >
                    <X className="w-5 h-5" />
                </button>
            )}
        </div>
    );
};

export default ErrorMessage;