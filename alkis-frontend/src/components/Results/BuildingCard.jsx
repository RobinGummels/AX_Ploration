import React from 'react';
import { Maximize2 } from 'lucide-react';
import { formatArea, formatFloors } from '../../utils/formatters';

// displays a buildings information: name, area, distance, floors

const BuildingCard = ({ building, isSelected, onToggle, onZoom }) => {
    const handleZoom = (e) => {
        e.stopPropagation();
        if (onZoom) {
            onZoom(building.id);
        }
    };

    return (
        <div
            className={`p-4 border-b border-gray-800 cursor-pointer hover:bg-gray-800 ${isSelected ? 'bg-gray-800 border-l-4 border-l-yellow-500' : ''
                }`}
            onClick={() => onToggle(building.id)}
        >
            <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                    <div className="font-semibold text-sm mb-1">{building.name}</div>
                    <div className="text-xs text-gray-400 flex items-center gap-1">
                        <span className="inline-block w-2 h-2 bg-gray-600 rounded-full" />
                        {building.type}
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    {onZoom && (
                        <button
                            onClick={handleZoom}
                            className="bg-blue-600 hover:bg-blue-700 p-1.5 rounded transition-colors"
                            title="Zoom to building"
                        >
                            <Maximize2 className="w-4 h-4" />
                        </button>
                    )}
                    <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => onToggle(building.id)}
                        onClick={(e) => e.stopPropagation()}
                        className="w-4 h-4"
                    />
                </div>
            </div>

            <div className="space-y-1 text-xs">
                <div className="flex items-center gap-2">
                    <span className="text-gray-400">📐</span>
                    {building.area !== 0 ? (<span>{formatArea(building.area)}</span>) : (<span>-</span>)}
                </div>
                {/* <div className="flex items-center gap-2">
                    <span className="text-gray-400">📊</span>
                    <span>{building.district}</span>
                </div> */}
                <div className="flex items-center gap-2">
                    <span className="text-gray-400">🏢</span>
                    {building.floors !== 0 ? (<span>{formatFloors(building.floors)}</span>) : (<span>-</span>)}
                </div>
            </div>
        </div>
    );
};

export default BuildingCard;