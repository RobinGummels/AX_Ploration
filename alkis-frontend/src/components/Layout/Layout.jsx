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
    const { messages, isLoading, sendMessage, buildings: chatBuildings, showThinking, setShowThinking, thinkingMessages, cypherQuery } = useChat();
    const {
        buildings,
        selectedIds,
        toggleSelection,
        selectAll
    } = useBuildings(chatBuildings);

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
                showThinking={showThinking}
                onToggleThinking={setShowThinking}
                thinkingMessages={thinkingMessages}
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
                cypherQuery={cypherQuery}
            />
        </div>
    );
};

export default Layout;