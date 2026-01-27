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



                    {/* Help Button */}
                    <button
                        className="p-2 hover:bg-gray-800 rounded transition-colors"
                        title="Help"
                        onClick={() => setShowHelpModal(true)}
                    >
                        <HelpCircle className="w-4 h-4" />
                    </button>

                </div>
            </div>

            {/* Help Modal */}
            <Modal
                isOpen={showHelpModal}
                onClose={() => setShowHelpModal(false)}
                title="Help"
            >
                <div className="space-y-4 text-gray-300">
                    <p>
                        This website was designed to help navigate the ALKIS building catalog of Berlin. In the catalog, each building has a code corresponding to its functionality. But because it is a complex and tedious task to navigate the ALKIS building catalog, AX_Ploration provides a chatbot that answers any questions you might have.
                    </p>
                    <p>
                        Overall, the website is split into three parts: the chat window on the left, the map and statistics tabs in the middle, and the results on the right. In the top row, you can find a download icon where you can export the building information of the buildings returned for a specfic question you asked, but this functionality also pops up later on again. Right next to it, the help icon must have led you right to this pop-up, where we have this neat little introduction to our website.
                    </p>
                    <p>
                        Within the chat window, you can type any question about the buildings in Berlin, and the chatbot will answer it. Additionally, you can tick the box in the bottom left corner to show the thinking process behind the chatbot's answer. The answer then pops up right under your question.
                    </p>
                    <p>
                        In the middle, the interactive map is the default tab. Here, you can AX_Plore Berlin at will, but note that as of now, AX_Ploration only includes information on the city districts Mitte, Pankow and Friedrichshain-Kreuzberg. After a query has been answered, the matched buildings are displayed on the map, and by clicking on them, further information is displayed in a pop-up. After switching to the statistics tab ...
                    </p>
                    <p>
                        The right side shows the results of a query. At the top, you can select a sorting method for the results listed below. This includes: ... (say here after implemented). You can also select all buildings or reject your current selection, as well as export the building information of all selected buildings as a GeoJSON. Then, the cypher query is displayed to show you exactly how the chatbot interpreted your question - this is helpful if you are not sure whether your question was interpreted correctly. Of course, it would be best if you knew a bit of SQL to make sense of the query. Below the cypher query, all buildings that are matching your question and that were returned by the chatbot are listed with detailed information. You can explore these in detail here or in the map, whichever way you prefer.
                    </p>
                    <p>
                        Have fun AX_Ploring! All the best, the team of AX_Ploration. :)
                    </p>
                </div>
            </Modal>
        </>
    );
};

export default Header;