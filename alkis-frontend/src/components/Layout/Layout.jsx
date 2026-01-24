import React, { useState } from 'react';
import ChatSidebar from '../Chat/ChatSidebar';
import Header from './Header';
import MapView from '../Map/MapView';
import StatisticsView from '../Statistics/StatisticsView';
import ResultsSidebar from '../Results/ResultsSidebar';
import { useChat } from '../../hooks/useChat';
import { useBuildings } from '../../hooks/useBuildings';

// main app container, combines all three panels (left, middle, right), manages state

const Layout = () => {
    const [activeTab, setActiveTab] = useState('map');
    const { messages, isLoading, sendMessage, buildings: chatBuildings } = useChat();
    const {
        buildings,
        selectedIds,
        toggleSelection,
        selectAll
    } = useBuildings(chatBuildings);

    // Mock query explanation, connect to backend
    const queryExplanation = {
        code: '2100',
        type: 'University',
        reason: 'Query matched "university" keyword',
        filters: ['Function: University (2100)', 'Area: ≥ 2,000 m²']
    };

    const handleTabChange = (tab) => {
        setActiveTab(tab);
    };

    return (
        <div className="flex h-screen bg-gray-950 text-white font-sans">
            {/* Left Sidebar: Chat */}
            <ChatSidebar
                messages={messages}
                onSendMessage={sendMessage}
                isLoading={isLoading}
            />

            {/* Center: Map/Statistics */}
            <div className="flex-1 flex flex-col">
                <Header
                    activeTab={activeTab}
                    onTabChange={handleTabChange}
                    buildings={buildings}
                    selectedIds={selectedIds}
                />

                <div className="flex-1 overflow-hidden">
                    {activeTab === 'map' ? (
                        <MapView buildings={buildings} selectedIds={selectedIds} />
                    ) : (
                        <StatisticsView buildings={buildings} />
                    )}
                </div>
            </div>

            {/* Right Sidebar: Results */}
            <ResultsSidebar
                buildings={buildings}
                selectedIds={selectedIds}
                onToggleSelection={toggleSelection}
                onSelectAll={selectAll}
                query={queryExplanation}
            />
        </div>
    );
};

export default Layout;