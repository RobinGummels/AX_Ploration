import React from 'react';
import { formatArea, formatDistance } from '../../utils/formatters';

// displays a buildings information: name, area, distance, floors

const BuildingCard = ({ building, isSelected, onToggle }) => {
    return (
        <div
            className={`p-4 border-b border-gray-800 cursor-pointer hover:bg-gray-800 ${isSelected ? 'bg-gray-800 border-l-4 border-l-blue-500' : ''
                }`}
            onClick={() => onToggle(building.id)}
        >
            <div className="flex items-start justify-between mb-2">
                <div>
                    <div className="font-semibold text-sm mb-1">{building.name}</div>
                    <div className="text-xs text-gray-400 flex items-center gap-1">
                        <span className="inline-block w-2 h-2 bg-gray-600 rounded-full" />
                        {building.type}
                    </div>
                </div>
                <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => onToggle(building.id)}
                    onClick={(e) => e.stopPropagation()}
                    className="w-4 h-4"
                />
            </div>

            <div className="space-y-1 text-xs">
                <div className="flex items-center gap-2">
                    <span className="text-gray-400">📐</span>
                    <span>{formatArea(building.area)}</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-gray-400">📍</span>
                    <span>{formatDistance(building.distance)}</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-gray-400">📊</span>
                    <span>{building.district}</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-gray-400">🏢</span>
                    <span>{building.floors} floors</span>
                </div>
            </div>
        </div>
    );
};

export default BuildingCard;