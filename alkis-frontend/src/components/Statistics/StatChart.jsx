import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// bar chart component 

const StatChart = ({ data, dataKey, xKey, title }) => {
    return (
        <div className="bg-gray-800 p-4 rounded">
            <h3 className="text-white font-semibold mb-3">{title}</h3>
            <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey={xKey} stroke="#9CA3AF" />
                    <YAxis stroke="#9CA3AF" />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1F2937',
                            border: '1px solid #374151',
                            borderRadius: '0.375rem'
                        }}
                    />
                    <Bar dataKey={dataKey} fill="#3B82F6" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

export default StatChart;