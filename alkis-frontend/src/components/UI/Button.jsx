import React from 'react';

// button component

const Button = ({
    children,
    onClick,
    variant = 'primary',
    size = 'md',
    className = '',
    ...props
}) => {
    const baseClasses = 'rounded font-medium transition-colors focus:outline-none focus:ring-2';

    const variants = {
        primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
        secondary: 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500',
        ghost: 'bg-transparent hover:bg-gray-800 text-gray-300',
    };

    const sizes = {
        sm: 'px-2 py-1 text-sm',
        md: 'px-4 py-2',
        lg: 'px-6 py-3 text-lg',
    };

    return (
        <button
            className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
            onClick={onClick}
            {...props}
        >
            {children}
        </button>
    );
};

export default Button;