import { useState, useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet-draw/dist/leaflet.draw.css';
import 'leaflet-draw';
import { MAP_CONFIG } from '../utils/constants';

// initializes leaflet map, renders building polygons and updates with changed selection 
// also provides drawing tools for polygon/point selection

export const useMap = (buildings, selectedIds, onDrawingChange) => {
    const mapRef = useRef(null);
    const mapInstanceRef = useRef(null);
    const layersRef = useRef({});
    const drawnItemsRef = useRef(null);

    useEffect(() => {
        if (!mapRef.current || mapInstanceRef.current) return;

        // Initialize map
        const map = L.map(mapRef.current, {
            zoomControl: false // Disable default zoom controls
        }).setView(MAP_CONFIG.center, MAP_CONFIG.zoom);

        // Add tile layer
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: MAP_CONFIG.maxZoom,
            minZoom: MAP_CONFIG.minZoom,
        }).addTo(map);

        mapInstanceRef.current = map;

        // Initialize drawing tools immediately after map creation
        initializeDrawing(map);

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
                        color: isSelected ? '#eab308' : '#dc2626',
                        fillColor: isSelected ? '#fcd34d' : '#ef4444',
                        fillOpacity: 0.7,
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

    const initializeDrawing = (map) => {
        // Create feature group for drawn items
        drawnItemsRef.current = new L.FeatureGroup();
        map.addLayer(drawnItemsRef.current);

        // Initialize Leaflet Draw
        const drawControl = new L.Control.Draw({
            position: 'bottomleft',
            draw: {
                polygon: true,
                polyline: false,
                rectangle: false,
                circle: false,
                marker: true,
                circlemarker: false,
            },
            edit: {
                featureGroup: drawnItemsRef.current,
                remove: true,
                edit: false,
            },
        });
        map.addControl(drawControl);

        // Handle drawing events
        map.on('draw:created', handleDrawingCreated);
        map.on('draw:edited', handleDrawingEdited);
        map.on('draw:deleted', handleDrawingDeleted);

        return drawControl;
    };

    const handleDrawingCreated = (e) => {
        // User draws geometry on map
        // Only allow one geometry at a time - clear previous ones
        const layer = e.layer;
        drawnItemsRef.current.clearLayers();
        drawnItemsRef.current.addLayer(layer);
        emitDrawingChange();
    };

    const handleDrawingEdited = () => {
        // User edits existing geometry
        emitDrawingChange();
    };

    const handleDrawingDeleted = () => {
        // User deletes geometry
        emitDrawingChange();
    };

    const emitDrawingChange = () => {
        // Convert to GeoJSON (WGS84 coordinates)
        // and pass it up to parent component (Layout) via callback
        if (onDrawingChange && drawnItemsRef.current) {
            const geojson = drawnItemsRef.current.toGeoJSON();
            onDrawingChange(geojson);
        }
    };

    const clearDrawing = () => {
        if (drawnItemsRef.current) {
            drawnItemsRef.current.clearLayers();
            if (onDrawingChange) {
                onDrawingChange(null);
            }
        }
    };

    const getDrawnGeometry = () => {
        if (drawnItemsRef.current && drawnItemsRef.current.getLayers().length > 0) {
            return drawnItemsRef.current.toGeoJSON();
        }
        return null;
    };

    return {
        mapRef,
        mapInstance: mapInstanceRef.current,
        initializeDrawing,
        clearDrawing,
        getDrawnGeometry,
    };
};