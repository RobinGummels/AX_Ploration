import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

// collapsible with query-matching 

const QueryExplanation = ({ cypherQuery }) => {
    const [isExpanded, setIsExpanded] = useState(true);


    return (
        <div className="border-b border-gray-800 p-4">
            <div className="font-semibold mb-2">Generated Cypher Query</div>

            {cypherQuery ? (
                <pre className="bg-gray-900 text-green-400 p-3 rounded overflow-x-auto whitespace-pre-wrap">
                    {cypherQuery}
                </pre>
            ) : (
                <div className="text-gray-500 italic">No query generated yet.</div>
            )}
        </div>
    );
};

export default QueryExplanation;