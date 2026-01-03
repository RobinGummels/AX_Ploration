/**
 * Convert building data to GeoJSON format
 * Mockup, change for actual ALKIS data structure later
 */
export const buildingsToGeoJSON = (buildings) => {
    const features = buildings.map(building => {
        // Mock coordinates 
        const mockCoordinates = generateMockCoordinates(building.id);

        return {
            type: "Feature",
            id: building.id,
            properties: {
                id: building.id,
                name: building.name,
                type: building.type,
                area: building.area,
                floors: building.floors,
                district: building.district,
                distance: building.distance,

            },
            geometry: {
                type: "Polygon",
                coordinates: [mockCoordinates] // Array of coordinate arrays
            }
        };
    });

    return {
        type: "FeatureCollection",
        features: features,
        metadata: {
            exportDate: new Date().toISOString(),
            totalBuildings: buildings.length,
            source: "ALKIS Berlin Building Database"
        }
    };
};

/**
 * mock coordinates for a building
 */
const generateMockCoordinates = (buildingId) => {
    const mockCoords = {
        1: [[13.393, 52.518], [13.395, 52.518], [13.395, 52.520], [13.393, 52.520], [13.393, 52.518]],
        2: [[13.327, 52.512], [13.329, 52.512], [13.329, 52.514], [13.327, 52.514], [13.327, 52.512]],
        3: [[13.328, 52.513], [13.329, 52.513], [13.329, 52.514], [13.328, 52.514], [13.328, 52.513]],
        4: [[13.353, 52.542], [13.355, 52.542], [13.355, 52.544], [13.353, 52.544], [13.353, 52.542]],
        5: [[13.290, 52.453], [13.292, 52.453], [13.292, 52.455], [13.290, 52.455], [13.290, 52.453]],
        6: [[13.408, 52.473], [13.410, 52.473], [13.410, 52.475], [13.408, 52.475], [13.408, 52.473]],
        7: [[13.527, 52.458], [13.529, 52.458], [13.529, 52.460], [13.527, 52.460], [13.527, 52.458]],
    };

    return mockCoords[buildingId] || [[13.4, 52.52], [13.41, 52.52], [13.41, 52.53], [13.4, 52.53], [13.4, 52.52]];
};

/**
 * Download GeoJSON as a file
 */
export const downloadGeoJSON = (geoJSON, filename = 'alkis-buildings.geojson') => {
    const jsonString = JSON.stringify(geoJSON, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Clean up the URL object
    URL.revokeObjectURL(url);
};

/**
 * Alternative: Export selected buildings only
 */
export const exportSelectedBuildings = (buildings, selectedIds) => {
    const selectedBuildings = buildings.filter(b => selectedIds.includes(b.id));
    const geoJSON = buildingsToGeoJSON(selectedBuildings);
    const filename = `alkis-buildings-selected-${selectedBuildings.length}.geojson`;
    downloadGeoJSON(geoJSON, filename);
};

/**
 * Alternative: Export all buildings
 */
export const exportAllBuildings = (buildings) => {
    const geoJSON = buildingsToGeoJSON(buildings);
    const filename = `alkis-buildings-all-${buildings.length}.geojson`;
    downloadGeoJSON(geoJSON, filename);
};