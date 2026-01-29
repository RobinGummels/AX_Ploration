import React, { useState } from 'react';
import { Download, List } from 'lucide-react';
import BuildingCard from './BuildingCard';
import QueryExplanation from './QueryExplanation';
import FilterBar from './FilterBar';
import Select from '../UI/Select';
import EmptyState from '../UI/EmptyState';
import Loading from '../UI/Loading';
import { exportSelectedBuildings } from '../../utils/exportUtils';

// right panel with building list, filters, export button

const ResultsSidebar = ({
    buildings,
    selectedIds,
    onToggleSelection,
    onSelectAll,
    cypherQuery,
    drawnGeometry,
    loading = false
}) => {
    const [sortBy, setSortBy] = useState('area');
    const [activeFilters, setActiveFilters] = useState([]);

    const sortOptions = [
        { value: 'area', label: 'Sort by Area' },
        { value: 'name', label: 'Sort by Name' },
        { value: 'floors', label: 'Sort by Floors' },
    ];

    const handleExport = () => {
        if (selectedIds.length === 0) {
            alert('No buildings selected. Please select buildings to export.');
            return;
        }
        console.log('Exporting:', selectedIds.length, 'buildings');
        exportSelectedBuildings(buildings, selectedIds);
    };

    const handleRemoveFilter = (filter) => {
        setActiveFilters(activeFilters.filter(f => f !== filter));
    };

    const handleClearAllFilters = () => {
        setActiveFilters([]);
    };

    // Sort buildings based on selected sort option
    const getSortedBuildings = () => {
        const buildingsCopy = [...buildings];
        
        switch (sortBy) {
            case 'area':
                return buildingsCopy.sort((a, b) => b.area - a.area);
            case 'name':
                return buildingsCopy.sort((a, b) => a.name.localeCompare(b.name));
            case 'floors':
                return buildingsCopy.sort((a, b) => b.floors - a.floors);
            default:
                return buildingsCopy;
        }
    };

    const sortedBuildings = getSortedBuildings();

    return (
        <div className="w-96 bg-gray-900 flex flex-col border-l border-gray-800">
            {/* Results Header */}
            <div className="p-4 border-b border-gray-800">
                <div className="flex items-center justify-between mb-3">
                    <h2 className="font-semibold">Results</h2>
                    <span className="text-sm text-gray-400">{buildings.length}</span>
                </div>

                <div className="flex items-center gap-2 mb-3">
                    <Select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                        options={sortOptions}
                        className="flex-1"
                    />
                    <button className="bg-gray-800 p-2 rounded hover:bg-gray-700">
                        <List className="w-4 h-4" />
                    </button>
                </div>

                <button
                    onClick={onSelectAll}
                    className="w-full bg-gray-800 py-2 rounded text-sm hover:bg-gray-700"
                >
                    Select all
                </button>

                <button
                    onClick={() => {
                        // Reject all by passing empty array
                        selectedIds.forEach(id => onToggleSelection(id));
                    }}
                    className="w-full bg-gray-800 py-2 rounded text-sm hover:bg-gray-700 mt-2"
                >
                    Reject all
                </button>

                <button
                    onClick={handleExport}
                    disabled={selectedIds.length === 0}
                    className="w-full bg-blue-600 py-2 rounded text-sm hover:bg-blue-700 mt-2 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <Download className="w-4 h-4" />
                    Export ({selectedIds.length})
                </button>
            </div>

            {/* Query Explanation*/}
            <QueryExplanation cypherQuery={cypherQuery} />

            {/* Filter Bar */}
            <FilterBar
                activeFilters={activeFilters}
                onRemoveFilter={handleRemoveFilter}
                onClearAll={handleClearAllFilters}
            />

            {/* Building List */}
            <div className="flex-1 overflow-y-auto">
                {loading ? (
                    <div className="flex items-center justify-center h-full">
                        <Loading text="Loading buildings..." />
                    </div>
                ) : buildings.length === 0 ? (
                    <EmptyState
                        title="No buildings found"
                        description="Try adjusting your search query"
                    />
                ) : (
                    // Display sorted building list
                    sortedBuildings.map((building) => (
                        <BuildingCard
                            key={building.id}
                            building={building}
                            isSelected={selectedIds.includes(building.id)}
                            onToggle={onToggleSelection}
                        />
                    ))
                )}
            </div>
        </div>
    );
};

export default ResultsSidebar;