import React from 'react';
import MetricCard from './MetricCard';
import StatChart from './StatChart';
import { formatArea } from '../../utils/formatters';

// statistics tab with metrics, charts 

const StatisticsView = ({ buildings }) => {
    const totalBuildings = buildings.length;
    const avgArea = buildings.length > 0
        ? Math.round(buildings.reduce((sum, b) => sum + b.area, 0) / buildings.length)
        : 0;
    const avgFloors = buildings.length > 0
        ? (buildings.reduce((sum, b) => sum + b.floors, 0) / buildings.length).toFixed(1)
        : 0;
    const uniqueDistricts = new Set(buildings.map(b => b.district)).size;

    const districtCounts = buildings.reduce((acc, building) => {
        acc[building.district] = (acc[building.district] || 0) + 1;
        return acc;
    }, {});

    // Prepare data for chart
    const chartData = Object.entries(districtCounts).map(([district, count]) => ({
        district,
        count
    }));

    return (
        <div className="w-full h-full bg-gray-900 p-6 overflow-y-auto">
            <h2 className="text-white text-2xl font-bold mb-6">Statistics</h2>

            <div className="grid grid-cols-2 gap-4 mb-6">
                <MetricCard label="Total Buildings" value={totalBuildings} />
                <MetricCard label="Average Area" value={formatArea(avgArea)} />
                <MetricCard label="Average Floors" value={avgFloors} />
                <MetricCard label="Districts Covered" value={uniqueDistricts} />
            </div>

            {/* Chart */}
            {buildings.length > 0 && (
                <div className="mb-4">
                    <StatChart
                        data={chartData}
                        dataKey="count"
                        xKey="district"
                        title="Buildings by District"
                    />
                </div>
            )}

            <div className="bg-gray-800 p-4 rounded mb-4">
                <h3 className="text-white font-semibold mb-3">Area Distribution</h3>
                <div className="space-y-2">
                    {buildings.map((building) => (
                        <div key={building.id}>
                            <div className="text-gray-400 text-sm mb-1">{building.name}</div>
                            <div className="w-full bg-gray-700 rounded-full h-2">
                                <div
                                    className="bg-blue-500 h-2 rounded-full"
                                    style={{ width: `${(building.area / Math.max(...buildings.map(b => b.area))) * 100}%` }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="bg-gray-800 p-4 rounded">
                <h3 className="text-white font-semibold mb-3">District Summary</h3>
                <div className="space-y-2">
                    {Object.entries(districtCounts).map(([district, count]) => (
                        <div key={district} className="flex justify-between text-sm">
                            <span className="text-gray-400">{district}</span>
                            <span className="text-white">{count}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default StatisticsView;