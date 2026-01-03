import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

// collapsible with query-matching 

const QueryExplanation = ({ query }) => {
    const [isExpanded, setIsExpanded] = useState(true);

    return (
        <div className="border-b border-gray-800">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full p-4 flex items-center justify-between hover:bg-gray-800"
            >
                <span className="font-semibold">Query Explanation</span>
                {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {isExpanded && query && (
                <div className="px-4 pb-4 text-sm space-y-2">
                    <div>
                        <div className="text-gray-400">Matched AX Code:</div>
                        <div className="text-blue-400">{query.code} - {query.type}</div>
                    </div>
                    <div>
                        <div className="text-gray-400">Reason:</div>
                        <div>{query.reason}</div>
                    </div>
                    {query.filters && query.filters.length > 0 && (
                        <div>
                            <div className="text-gray-400">Active Filters:</div>
                            <div className="space-y-1">
                                {query.filters.map((filter, idx) => (
                                    <div key={idx} className="bg-gray-800 px-2 py-1 rounded inline-block mr-2">
                                        {filter}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default QueryExplanation;