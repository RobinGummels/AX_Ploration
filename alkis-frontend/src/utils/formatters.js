// convert buildings to GeoJSON and download as file

export const formatArea = (area) => {
    return `${area.toLocaleString('de-DE')} m²`;
};

export const formatDistance = (distance) => {
    return `${distance.toFixed(2)} km`;
};

export const formatFloors = (floors) => {
    return `${floors} ${floors === 1 ? 'floor' : 'floors'}`;
};