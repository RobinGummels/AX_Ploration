import React from 'react';
import { X, MapPin, Ruler, Layers } from 'lucide-react';
import { formatArea, formatDistance, formatFloors } from '../../utils/formatters';

// like BuildingCard, more detailed

const BuildingDetailModal = ({ building, onClose }) => {
    if (!building) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[2000]">
            <div className="bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-700">
                    <h2 className="text-xl font-bold text-white">{building.name}</h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Basic Info */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-3">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center">
                                    <Ruler className="w-5 h-5 text-blue-400" />
                                </div>
                                <div>
                                    <div className="text-sm text-gray-400">Area</div>
                                    <div className="text-white font-semibold">{formatArea(building.area)}</div>
                                </div>
                            </div>

                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center">
                                    <Layers className="w-5 h-5 text-blue-400" />
                                </div>
                                <div>
                                    <div className="text-sm text-gray-400">Floors</div>
                                    <div className="text-white font-semibold">{building.floors}</div>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-3">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center">
                                    <MapPin className="w-5 h-5 text-blue-400" />
                                </div>
                                <div>
                                    <div className="text-sm text-gray-400">Distance</div>
                                    <div className="text-white font-semibold">{formatDistance(building.distance)}</div>
                                </div>
                            </div>

                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center">
                                    <span className="text-blue-400">📊</span>
                                </div>
                                <div>
                                    <div className="text-sm text-gray-400">District</div>
                                    <div className="text-white font-semibold">{building.district}</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Additional Info */}
                    <div className="border-t border-gray-700 pt-4">
                        <h3 className="text-sm font-semibold text-gray-400 mb-3">Additional Information</h3>
                        <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                                <span className="text-gray-400">Type:</span>
                                <span className="text-white">{building.type}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-400">Building ID:</span>
                                <span className="text-white">{building.id}</span>
                            </div>
                            {building.yearBuilt && (
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Year Built:</span>
                                    <span className="text-white">{building.yearBuilt}</span>
                                </div>
                            )}
                            {building.address && (
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Address:</span>
                                    <span className="text-white">{building.address}</span>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="border-t border-gray-700 pt-4 flex gap-3">
                        <button className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded">
                            View on Map
                        </button>
                        <button className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded">
                            Export Data
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default BuildingDetailModal;