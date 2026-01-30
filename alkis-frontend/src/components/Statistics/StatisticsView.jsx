import React from 'react';
import MetricCard from './MetricCard';
import StatChart from './StatChart';
import { formatArea, formatFloors } from '../../utils/formatters';

// statistics tab with metrics, charts 

const StatisticsView = ({ statistics }) => {
    const area_max = statistics?.area_max || "-";
    const area_mean = statistics?.area_mean || "-";
    const area_min = statistics?.area_min || "-";
    const building_count = statistics?.building_count || "-";
    const floors_above_max = statistics?.floors_above_max || "-";
    const floors_above_mean = statistics?.floors_above_mean || "-";
    const floors_above_min = statistics?.floors_above_min || "-";
    const house_number_min = statistics?.house_number_min || "-";
    const house_number_max = statistics?.house_number_max || "-";

    return (
        <div className="w-full h-full bg-gray-900 p-6 overflow-y-auto">
            <h2 className="text-white text-2xl font-bold mb-6">Statistics</h2>

            <div className="grid grid-cols-2 gap-4 mb-6">
                <MetricCard label="Total Buildings" value={building_count} />
                {area_mean !== "-" ? <MetricCard label="Average Area" value={formatArea(area_mean)} /> : <MetricCard label="Average Area" value={area_mean} />}
                {area_min !== "-" ? <MetricCard label="Min. Area" value={formatArea(area_min)} /> : <MetricCard label="Min. Area" value={area_min} />}
                {area_max !== "-" ? <MetricCard label="Max. Area" value={formatArea(area_max)} /> : <MetricCard label="Max. Area" value={area_max} />} 
                {floors_above_min !== "-" ? <MetricCard label="Min. Floors" value={formatFloors(floors_above_min)} /> : <MetricCard label="Min. Floors" value={floors_above_min} />}
                {floors_above_max !== "-" ? <MetricCard label="Max. Floors" value={formatFloors(floors_above_max)} /> : <MetricCard label="Max. Floors" value={floors_above_max} />}
                {floors_above_mean !== "-" ? <MetricCard label="Average Floors" value={formatFloors(floors_above_mean)} /> : <MetricCard label="Average Floors" value={floors_above_mean} />}
                <MetricCard label="Min. House Number" value={house_number_min} />
                <MetricCard label="Max. House Number" value={house_number_max} />
            </div>

            {/* Chart
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
            </div> */}
        </div>
    );
};

export default StatisticsView;