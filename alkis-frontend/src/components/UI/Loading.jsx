import React from 'react';

// loading spinner 

const Loading = ({ size = 'md', text = 'Loading...' }) => {
    const sizes = {
        sm: 'w-4 h-4',
        md: 'w-8 h-8',
        lg: 'w-12 h-12'
    };

    return (
        <div className="flex flex-col items-center justify-center gap-2">
            <div className={`${sizes[size]} border-4 border-gray-700 border-t-blue-500 rounded-full animate-spin`} />
            {text && <p className="text-gray-400 text-sm">{text}</p>}
        </div>
    );
};

export default Loading;