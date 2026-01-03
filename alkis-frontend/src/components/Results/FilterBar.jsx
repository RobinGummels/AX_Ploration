import React from 'react';
import { Filter, X } from 'lucide-react';

// display and remove active filters

const FilterBar = ({ activeFilters, onRemoveFilter, onClearAll }) => {
    if (!activeFilters || activeFilters.length === 0) return null;

    return (
        <div className="p-3 border-b border-gray-800 bg-gray-850">
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 text-sm text-gray-400">
                    <Filter className="w-4 h-4" />
                    <span>Active Filters ({activeFilters.length})</span>
                </div>
                <button
                    onClick={onClearAll}
                    className="text-xs text-blue-400 hover:text-blue-300"
                >
                    Clear all
                </button>
            </div>
            <div className="flex flex-wrap gap-2">
                {activeFilters.map((filter, idx) => (
                    <div
                        key={idx}
                        className="bg-gray-800 px-2 py-1 rounded text-xs flex items-center gap-2"
                    >
                        <span>{filter.label}</span>
                        <button
                            onClick={() => onRemoveFilter(filter)}
                            className="hover:text-red-400"
                        >
                            <X className="w-3 h-3" />
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default FilterBar;