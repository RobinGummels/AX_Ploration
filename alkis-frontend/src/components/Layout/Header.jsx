import React, { useState } from 'react';
import { MapPin, BarChart3, Download, Settings, HelpCircle, User, ChevronDown } from 'lucide-react';
import { exportAllBuildings, exportSelectedBuildings } from '../../utils/exportUtils';
import Modal from '../UI/Modal';

// top navigation bar with tabs and buttons 

const Header = ({ activeTab, onTabChange, buildings = [], selectedIds = [] }) => {
    const [showExportMenu, setShowExportMenu] = useState(false);
    const [showSettingsModal, setShowSettingsModal] = useState(false);
    const [showHelpModal, setShowHelpModal] = useState(false);
    const [showAccountModal, setShowAccountModal] = useState(false);

    const handleExportAll = () => {
        console.log('Export All clicked, buildings:', buildings);
        if (buildings.length === 0) {
            alert('No buildings to export. Please perform a search first.');
            return;
        }
        exportAllBuildings(buildings);
        setShowExportMenu(false);
    };

    const handleExportSelected = () => {
        console.log('Export Selected clicked, selectedIds:', selectedIds);
        if (selectedIds.length === 0) {
            alert('No buildings selected. Please select buildings from the results panel.');
            return;
        }
        exportSelectedBuildings(buildings, selectedIds);
        setShowExportMenu(false);
    };

    return (
        <>
            <div className="bg-gray-900 border-b border-gray-800 px-4 py-3 flex items-center justify-between relative z-[1001]">
                <div className="flex gap-2">
                    <button
                        onClick={() => onTabChange('map')}
                        className={`flex items-center gap-2 px-4 py-2 rounded transition-colors ${activeTab === 'map'
                            ? 'bg-gray-800 text-white border-b-2 border-blue-500'
                            : 'text-gray-400 hover:text-white hover:bg-gray-800'
                            }`}
                    >
                        <MapPin className="w-4 h-4" />
                        Map
                    </button>
                    <button
                        onClick={() => onTabChange('statistics')}
                        className={`flex items-center gap-2 px-4 py-2 rounded transition-colors ${activeTab === 'statistics'
                            ? 'bg-gray-800 text-white border-b-2 border-blue-500'
                            : 'text-gray-400 hover:text-white hover:bg-gray-800'
                            }`}
                    >
                        <BarChart3 className="w-4 h-4" />
                        Statistics
                    </button>
                </div>

                <div className="flex items-center gap-2">
                    {/* Export Dropdown */}
                    <div className="relative">
                        <button
                            className="p-2 hover:bg-gray-800 rounded transition-colors flex items-center gap-1"
                            title="Export GeoJSON"
                            onClick={() => setShowExportMenu(!showExportMenu)}
                        >
                            <Download className="w-4 h-4" />
                            <ChevronDown className="w-3 h-3" />
                        </button>

                        {showExportMenu && (
                            <>
                                {/* Backdrop to close menu */}
                                <div
                                    className="fixed inset-0 z-[1100]"
                                    onClick={() => setShowExportMenu(false)}
                                />

                                {/* Dropdown menu */}
                                <div className="absolute right-0 mt-2 w-56 bg-gray-800 rounded-lg shadow-lg border border-gray-700 py-2 z-[1101]">
                                    <button
                                        onClick={handleExportAll}
                                        className="w-full text-left px-4 py-2 hover:bg-gray-700 transition-colors flex items-center justify-between"
                                    >
                                        <span>Export All Results</span>
                                        <span className="text-xs text-gray-400">({buildings.length})</span>
                                    </button>
                                    <button
                                        onClick={handleExportSelected}
                                        className="w-full text-left px-4 py-2 hover:bg-gray-700 transition-colors flex items-center justify-between"
                                        disabled={selectedIds.length === 0}
                                    >
                                        <span className={selectedIds.length === 0 ? 'text-gray-500' : ''}>
                                            Export Selected
                                        </span>
                                        <span className="text-xs text-gray-400">({selectedIds.length})</span>
                                    </button>

                                    <div className="border-t border-gray-700 my-2" />

                                    <div className="px-4 py-2 text-xs text-gray-400">
                                        Format: GeoJSON
                                    </div>
                                </div>
                            </>
                        )}
                    </div>

                    {/* Settings Button */}
                    <button
                        className="p-2 hover:bg-gray-800 rounded transition-colors"
                        title="Settings"
                        onClick={() => setShowSettingsModal(true)}
                    >
                        <Settings className="w-4 h-4" />
                    </button>

                    {/* Help Button */}
                    <button
                        className="p-2 hover:bg-gray-800 rounded transition-colors"
                        title="Help"
                        onClick={() => setShowHelpModal(true)}
                    >
                        <HelpCircle className="w-4 h-4" />
                    </button>

                    {/* Account Button */}
                    <button
                        className="p-2 hover:bg-gray-800 rounded transition-colors"
                        title="Account"
                        onClick={() => setShowAccountModal(true)}
                    >
                        <User className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Settings Modal */}
            <Modal
                isOpen={showSettingsModal}
                onClose={() => setShowSettingsModal(false)}
                title="Settings"
            >
                <div className="space-y-4 text-gray-300">
                    <p>
                        Here, you can change your settings.
                    </p>
                </div>
            </Modal>

            {/* Help Modal */}
            <Modal
                isOpen={showHelpModal}
                onClose={() => setShowHelpModal(false)}
                title="Help"
            >
                <div className="space-y-4 text-gray-300">
                    <p>
                        If you need help, feel free to contact us at: ...
                    </p>
                </div>
            </Modal>

            {/* Account Modal */}
            <Modal
                isOpen={showAccountModal}
                onClose={() => setShowAccountModal(false)}
                title="Account"
            >
                <div className="space-y-4 text-gray-300">
                    <p>
                        Welcome to your account!
                    </p>
                </div>
            </Modal>
        </>
    );
};

export default Header;