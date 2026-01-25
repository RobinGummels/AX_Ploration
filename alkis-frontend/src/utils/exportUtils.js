/**
 * Convert building data to GeoJSON format
 * Expects building objects with geometry (GeoJSON object) and metadata fields
 */
export const buildingsToGeoJSON = (buildings) => {
    console.log('buildingsToGeoJSON called with:', buildings);
    const features = buildings.map((building, idx) => {
        // console.log(`Processing building ${idx}:`, building);
        // Use the parsed geometry if available, otherwise skip
        if (!building.geometry) {
            console.log(`Building ${idx} has no geometry, skipping`);
            return null;
        }

        return {
            type: "Feature",
            id: building.id,
            properties: {
                id: building.id,
                name: building.name,
                area: building.area,
                floors: building.floors,
                district: building.district,
                centroid: building.centroid,
            },
            geometry: building.geometry
        };
    }).filter(Boolean);

    console.log('Generated features:', features);
    const result = {
        type: "FeatureCollection",
        features: features,
        metadata: {
            exportDate: new Date().toISOString(),
            totalBuildings: features.length,
            source: "ALKIS Berlin Building Database"
        }
    };
    console.log('Final GeoJSON:', result);
    return result;
};

/**
 * Download GeoJSON as a file
 */
export const downloadGeoJSON = (geoJSON, filename = 'alkis-buildings.geojson') => {
    try {
        const jsonString = JSON.stringify(geoJSON, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.style.display = 'none';
        
        // Ensure link is in the DOM before clicking
        document.body.appendChild(link);
        link.click();
        
        // Clean up after a small delay to ensure the download is queued
        setTimeout(() => {
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }, 100);
        
        console.log(`Export successful: ${filename}`);
    } catch (error) {
        console.error('Export failed:', error);
        alert('Failed to export buildings. Please try again.');
    }
};

/**
 * Alternative: Export selected buildings only
 */
export const exportSelectedBuildings = (buildings, selectedIds) => {
    try {
        const selectedBuildings = buildings.filter(b => selectedIds.includes(b.id));
        if (selectedBuildings.length === 0) {
            alert('No buildings to export.');
            return;
        }
        const geoJSON = buildingsToGeoJSON(selectedBuildings);
        const filename = `alkis-buildings-selected-${selectedBuildings.length}.geojson`;
        downloadGeoJSON(geoJSON, filename);
    } catch (error) {
        console.error('Export error:', error);
        alert('Error exporting buildings.');
    }
};

/**
 * Alternative: Export all buildings
 */
export const exportAllBuildings = (buildings) => {
    try {
        console.log('exportAllBuildings called, buildings count:', buildings.length);
        if (!buildings || buildings.length === 0) {
            alert('No buildings to export.');
            return;
        }
        console.log('Creating GeoJSON...');
        const geoJSON = buildingsToGeoJSON(buildings);
        console.log('GeoJSON created, starting download...');
        const filename = `alkis-buildings-all-${buildings.length}.geojson`;
        downloadGeoJSON(geoJSON, filename);
        console.log('Download initiated');
    } catch (error) {
        console.error('Export error:', error);
        alert('Error exporting buildings.');
    }
};