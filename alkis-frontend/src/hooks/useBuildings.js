import { useState, useEffect } from 'react';
import { buildingsAPI } from '../services/api';

// manages building data, selection state and fetching logic

export const useBuildings = (initialQuery = null) => {
    const [buildings, setBuildings] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedIds, setSelectedIds] = useState([]);

    const fetchBuildings = async (query) => {
        setLoading(true);
        setError(null);
        try {
            const data = await buildingsAPI.search(query);
            setBuildings(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (initialQuery) {
            fetchBuildings(initialQuery);
        }
    }, []);

    const toggleSelection = (id) => {
        setSelectedIds(prev =>
            prev.includes(id)
                ? prev.filter(i => i !== id)
                : [...prev, id]
        );
    };

    const selectAll = () => {
        setSelectedIds(buildings.map(b => b.id));
    };

    const deselectAll = () => {
        setSelectedIds([]);
    };

    return {
        buildings,
        loading,
        error,
        selectedIds,
        toggleSelection,
        selectAll,
        deselectAll,
        refetch: fetchBuildings,
    };
};