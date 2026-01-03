import React from 'react';

// dropdown component 

const Select = ({ value, onChange, options, className = '', ...props }) => {
    return (
        <select
            value={value}
            onChange={onChange}
            className={`bg-gray-800 text-white rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600 ${className}`}
            {...props}
        >
            {options.map(option => (
                <option key={option.value} value={option.value}>
                    {option.label}
                </option>
            ))}
        </select>
    );
};

export default Select;