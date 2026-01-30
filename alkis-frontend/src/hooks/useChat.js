import { useState, useEffect } from 'react';
import proj4 from 'proj4';
import { chatAPI } from '../services/api';
// import websocketService from '../services/websocket';

// manages chat messages, loading state and sending messages

// Register projection once so proj4 can parse EPSG:25833 payloads from backend
if (!proj4.defs('EPSG:25833')) {
    proj4.defs('EPSG:25833', '+proj=utm +zone=33 +ellps=GRS80 +datum=ETRS89 +units=m +no_defs');
}

// Define transformers: EPSG:25833 (UTM 33N meters) <-> EPSG:4326 (lon/lat)
const toWgs84 = proj4('EPSG:25833', 'EPSG:4326');
const fromWgs84 = proj4('EPSG:4326', 'EPSG:25833');

// Recursively transform coordinates (Polygon / MultiPolygon)
const transformCoordinates = (coords) => {
    if (!Array.isArray(coords)) return coords;
    if (typeof coords[0] === 'number') {
        return toWgs84.forward(coords); // [lon, lat]
    }
    return coords.map(transformCoordinates);
};

// Transform coordinates from WGS84 to UTM 33N for backend
const transformCoordinatesToUtm = (coords) => {
    if (!Array.isArray(coords)) return coords;
    if (typeof coords[0] === 'number') {
        return fromWgs84.forward(coords); // [x, y] in UTM
    }
    return coords.map(transformCoordinatesToUtm);
};

// Convert GeoJSON geometry to WKT format in EPSG:25833
const geojsonToWkt = (geometry) => {
    if (!geometry) return null;

    const type = geometry.type;
    const coords = geometry.coordinates;

    if (!coords) return null;

    // Transform coordinates from WGS84 to UTM 33N
    const utmCoords = transformCoordinatesToUtm(coords);

    switch (type) {
        case 'Point':
            return `POINT (${utmCoords[0]} ${utmCoords[1]})`;
        
        case 'Polygon':
            const polyRings = utmCoords.map(ring => {
                const ringCoords = ring.map(c => `${c[0]} ${c[1]}`).join(', ');
                return `(${ringCoords})`;
            }).join(', ');
            return `POLYGON (${polyRings})`;
        
        default:
            console.warn('Unsupported geometry type:', type);
            return null;
    }
};

// Normalize possible Feature/FeatureCollection to Geometry object and transform
const transformGeometryToWgs84 = (geoJson) => {
    if (!geoJson) return null;

    // If FeatureCollection, take first feature geometry
    if (geoJson.type === 'FeatureCollection' && Array.isArray(geoJson.features) && geoJson.features.length > 0) {
        return transformGeometryToWgs84(geoJson.features[0].geometry);
    }

    // If Feature, use its geometry
    if (geoJson.type === 'Feature' && geoJson.geometry) {
        return transformGeometryToWgs84(geoJson.geometry);
    }

    if (!geoJson.coordinates) return geoJson;

    return {
        ...geoJson,
        coordinates: transformCoordinates(geoJson.coordinates),
    };
};

const parseCentroid = (centroidWkt) => {
    if (!centroidWkt || typeof centroidWkt !== 'string') return null;
    const match = centroidWkt.match(/Point\s*\(\s*([\d.+-]+)\s+([\d.+-]+)\s*\)/i);
    if (!match) return null;
    const x = parseFloat(match[1]);
    const y = parseFloat(match[2]);
    const [lon, lat] = toWgs84.forward([x, y]);
    return { lat, lon };
};

const parseBuildings = (results) => {
    const buildings = results[0].buildings || [];
    console.log("raw buildings from backend:", buildings);

    return buildings.map((item, index) => {
        try {
            if (index == 0) {
                console.log("parsing building entry:", item);
            }
            const geoJsonString = item?.geometry_geojson;
            if (!geoJsonString) return null;

            const geoJson = JSON.parse(geoJsonString);
            const geometry = transformGeometryToWgs84(geoJson);
            const centroid = parseCentroid(item?.centroid);

            return {
                id: item?.id ?? index,
                name: item?.name || item?.street_name || 'Building',
                geometry,
                area: item?.area ? Number(item.area) : 0,
                floors: item?.floors_above ?? 0,
                centroid,
            };
        } catch (error) {
            console.error('Error parsing building entry:', error, item);
            return null;
        }
    }).filter(Boolean);
};

export const useChat = (drawnGeometry) => {
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: 'Welcome to AX_Ploration. Ask questions about ALKIS building data in Berlin.'
        }
    ]);
    const [isLoading, setIsLoading] = useState(false);
    const [buildings, setBuildings] = useState([]);
    const [showThinking, setShowThinking] = useState(false);
    const [thinkingMessages, setThinkingMessages] = useState([]);
    const [cypherQuery, setCypherQuery] = useState(null);
    const [statistics, setStatistics] = useState(null);

    const sendMessage = async (content) => {
        // Add user message
        const userMessage = { role: 'user', content };
        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);
        setThinkingMessages([]);

        try {
            // Mock response until backend is ready
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 1000));

            /* Mock response based on query
            let mockResponse = "I understand you're asking about ALKIS building data. Your backend will process this query once connected.";

            if (content.toLowerCase().includes('university')) {
                mockResponse = "Found 8 university buildings with area ≥ 2,000 m². Once your backend is connected, I'll show you real results from the Neo4j database.";
            } else if (content.toLowerCase().includes('school')) {
                mockResponse = "Searching for school buildings in the ALKIS database...";
            } else if (content.toLowerCase().includes('area')) {
                mockResponse = "I can help you filter buildings by area. Please specify the criteria.";
            }

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: mockResponse
            }]);
            */

            //uncomment when backend connected:


            // Build query payload with optional spatial filter
            const queryPayload = {
                query: content,
                stream: showThinking,
            };

            // Convert drawn geometry to WKT format
            // Transform from GeoJSON (WGS84 - map coordinates)
            // to WKT in EPSG:25833 (UTM 33N - backend coordinate system)
            if (drawnGeometry && drawnGeometry.features && drawnGeometry.features.length > 0) {
                const geometry = drawnGeometry.features[0].geometry;
                const wktGeometry = geojsonToWkt(geometry);
                if (wktGeometry) {
                    queryPayload.spatial_filter = wktGeometry;
                    console.log('Spatial filter WKT:', wktGeometry);
                }
            }

            // const response = await chatAPI.sendMessage(content);
            const { final_answer: final_answer, results: results, cypher_query: cypher_query, } = await chatAPI.sendMessage(
                queryPayload,
                showThinking,
                (thinkingMsg) => setThinkingMessages(prev => [...prev, thinkingMsg])
            );
            console.log("final_answer", final_answer);
            console.log("cypher_query", cypher_query);
            console.log("results", results);
            console.log("statistics", results[0].statistics);
            setCypherQuery(cypher_query);
            setStatistics(results[0].statistics);

            // Only process buildings if results exist
            if (results) {
                const processedBuildings = parseBuildings(results);
                console.log("processedBuildings", processedBuildings);
                setBuildings(processedBuildings);
            } else {
                console.warn("No results received from backend");
                setBuildings([]);
            }

            if (final_answer) {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: final_answer
                }]);
            }


        } catch (error) {
            console.error('Error sending message:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please make sure the backend is running and try again.'
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return {
        messages,
        isLoading,
        sendMessage,
        buildings,
        showThinking,
        setShowThinking,
        thinkingMessages,
        cypherQuery,
        statistics,
    };
};
