import React from 'react';
import { ZoomIn, ZoomOut, Maximize2, Layers } from 'lucide-react';
import { useMap } from '../../hooks/useMap';

// zoom buttons and layer toggles, see problem below
// maybe have to change this, currently not used by MapView.jsx, have to clean this or delete it

const MapControls = ({ mapInstance, onToggleLayers }) => {
    if (!mapInstance) return null;

    const handleZoomIn = () => {
        if (mapInstance) mapInstance.zoomIn();
    };

    const handleZoomOut = () => {
        if (mapInstance) mapInstance.zoomOut();
    };

    const handleFitBounds = () => {
        if (mapInstance) {
            // Fit to all layers
            const bounds = mapInstance.getBounds();
            mapInstance.fitBounds(bounds);
        }
    };

    return (
        <div className="absolute top-4 right-4 flex flex-col gap-2 z-[1000]">
            <button
                onClick={handleZoomIn}
                className="bg-white hover:bg-gray-100 p-2 rounded shadow-lg"
                title="Zoom In"
            >
                <ZoomIn className="w-5 h-5 text-gray-700" />
            </button>
            <button
                onClick={handleZoomOut}
                className="bg-white hover:bg-gray-100 p-2 rounded shadow-lg"
                title="Zoom Out"
            >
                <ZoomOut className="w-5 h-5 text-gray-700" />
            </button>
            <button
                onClick={handleFitBounds}
                className="bg-white hover:bg-gray-100 p-2 rounded shadow-lg"
                title="Fit to Bounds"
            >
                <Maximize2 className="w-5 h-5 text-gray-700" />
            </button>
            <button
                onClick={onToggleLayers}
                className="bg-white hover:bg-gray-100 p-2 rounded shadow-lg"
                title="Toggle Layers"
            >
                <Layers className="w-5 h-5 text-gray-700" />
            </button>
        </div>
    );
};

const MapView = ({ buildings, selectedIds }) => {
    const { mapRef, mapInstance } = useMap(buildings, selectedIds);

    const handleToggleLayers = () => {
        console.log('Toggle layers');
        /* Implement layer toggle logic
        * could be for showing different stuff on the map, can also be deleted if not 
        * necessary
        */
    };

    return (
        <div className="relative w-full h-full">
            <div ref={mapRef} className="w-full h-full" />

            {/* Map Controls: only show when map is ready */}
            {mapInstance && (
                <MapControls
                    mapInstance={mapInstance}
                    onToggleLayers={handleToggleLayers}
                />
            )}

            {/* Legend */}
            <div className="absolute bottom-4 left-4 bg-white bg-opacity-95 p-3 rounded shadow-lg text-sm z-[1000]">
                <div className="font-semibold mb-2 text-gray-900">Legend</div>
                <div className="flex items-center gap-2 mb-1">
                    <div className="w-4 h-4 bg-gray-400 border-2 border-gray-600" />
                    <span className="text-gray-900">Building polygons</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-blue-700 border-2 border-blue-400" />
                    <span className="text-gray-900">Selected</span>
                </div>
            </div>
        </div>
    );
};

export default MapControls;