import React from 'react';

// single metric display card 

const MetricCard = ({ label, value, icon }) => {
    return (
        <div className="bg-gray-800 p-4 rounded">
            <div className="flex items-center justify-between mb-2">
                <div className="text-gray-400 text-sm">{label}</div>
                {icon && <div className="text-gray-500">{icon}</div>}
            </div>
            <div className="text-white text-3xl font-bold">{value}</div>
        </div>
    );
};

export default MetricCard;