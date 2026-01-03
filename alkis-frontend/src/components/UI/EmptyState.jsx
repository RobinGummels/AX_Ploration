import React from 'react';
import { Search } from 'lucide-react';

// "no results" placeholder with icon and message 

const EmptyState = ({
    icon: Icon = Search,
    title = 'No results found',
    description = 'Try adjusting your search or filters',
    action
}) => {
    return (
        <div className="flex flex-col items-center justify-center p-8 text-center">
            <div className="w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center mb-4">
                <Icon className="w-8 h-8 text-gray-500" />
            </div>
            <h3 className="text-lg font-semibold text-gray-300 mb-2">{title}</h3>
            <p className="text-sm text-gray-500 mb-4">{description}</p>
            {action && (
                <button
                    onClick={action.onClick}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm"
                >
                    {action.label}
                </button>
            )}
        </div>
    );
};

export default EmptyState;