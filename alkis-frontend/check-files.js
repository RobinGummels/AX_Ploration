const fs = require('fs');
const path = require('path');

const requiredFiles = [
    'index.html',
    'vite.config.js',
    'package.json',
    'src/main.jsx',
    'src/App.jsx',
    'src/styles/global.css',
    'src/components/Layout/Layout.jsx',
];

console.log('Checking required files...\n');

requiredFiles.forEach(file => {
    const exists = fs.existsSync(path.join(__dirname, file));
    console.log(`${exists ? '✅' : '❌'} ${file}`);
});