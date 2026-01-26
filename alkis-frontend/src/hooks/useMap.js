import { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import { MAP_CONFIG } from '../utils/constants';

// initializes leaflet map, renders building polygons and updates with changed selection 

export const useMap = (buildings, selectedIds) => {
    const mapRef = useRef(null);
    const mapInstanceRef = useRef(null);
    const layersRef = useRef({});

    useEffect(() => {
        if (!mapRef.current || mapInstanceRef.current) return;

        // Initialize map
        const map = L.map(mapRef.current).setView(MAP_CONFIG.center, MAP_CONFIG.zoom);

        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: MAP_CONFIG.maxZoom,
            minZoom: MAP_CONFIG.minZoom,
        }).addTo(map);

        mapInstanceRef.current = map;

        return () => {
            if (mapInstanceRef.current) {
                mapInstanceRef.current.remove();
                mapInstanceRef.current = null;
            }
        };
    }, []);

    useEffect(() => {
        if (!mapInstanceRef.current || !buildings.length) return;

        // Clear existing layers
        Object.values(layersRef.current).forEach(layer => {
            mapInstanceRef.current.removeLayer(layer);
        });
        layersRef.current = {};

        // Add building polygons
        buildings.forEach(building => {
            if (building.geometry) {
                const isSelected = selectedIds.includes(building.id);

                // Let Leaflet handle GeoJSON coordinate order (lon/lat)
                const layer = L.geoJSON(building.geometry, {
                    style: () => ({
                        color: isSelected ? '#3b82f6' : '#6b7280',
                        fillColor: isSelected ? '#1e40af' : '#374151',
                        fillOpacity: 0.6,
                        weight: 2,
                    })
                }).addTo(mapInstanceRef.current);

                layer.bindPopup(`
          <div style="color: black;">
            <strong>${building.name}</strong><br/>
            Area: ${Number(building.area).toLocaleString()} m²<br/>
            Floors: ${building.floors}<br/>
          </div>
        `);

                layersRef.current[building.id] = layer;
            }
        });

        // Fit bounds to show all buildings
        if (buildings.length > 0) {
            const group = L.featureGroup(Object.values(layersRef.current));
            mapInstanceRef.current.fitBounds(group.getBounds());
        }
    }, [buildings, selectedIds]);

    return { mapRef, mapInstance: mapInstanceRef.current };
};