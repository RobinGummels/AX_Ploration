import React from 'react';

// tab navigation

const Tabs = ({ tabs, activeTab, onChange }) => {
    return (
        <div className="flex gap-2 border-b border-gray-800">
            {tabs.map((tab) => (
                <button
                    key={tab.id}
                    onClick={() => onChange(tab.id)}
                    className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${activeTab === tab.id
                        ? 'border-blue-500 text-white'
                        : 'border-transparent text-gray-400 hover:text-white'
                        }`}
                >
                    {tab.icon && <tab.icon className="w-4 h-4" />}
                    {tab.label}
                </button>
            ))}
        </div>
    );
};

export default Tabs;