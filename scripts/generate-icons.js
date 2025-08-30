const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const iconDir = path.join(__dirname, '..', 'src-tauri', 'icons');

// Ensure icons directory exists
if (!fs.existsSync(iconDir)) {
  fs.mkdirSync(iconDir, { recursive: true });
}

// Create a simple blue square with "AI" text as SVG
const svgIcon = (size) => `
<svg width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg">
  <rect width="${size}" height="${size}" fill="#2563eb"/>
  <text x="50%" y="50%" font-family="Arial, sans-serif" font-size="${size * 0.4}" 
        fill="white" text-anchor="middle" dominant-baseline="middle" font-weight="bold">AI</text>
</svg>
`;

// Generate PNG icons
const sizes = [
  { name: '32x32.png', size: 32 },
  { name: '128x128.png', size: 128 },
  { name: '128x128@2x.png', size: 256 },
];

async function generateIcons() {
  for (const { name, size } of sizes) {
    const outputPath = path.join(iconDir, name);
    await sharp(Buffer.from(svgIcon(size)))
      .png()
      .toFile(outputPath);
    console.log(`Generated ${name}`);
  }
  
  // Create .ico file (Windows) - just copy 32x32 for now
  fs.copyFileSync(
    path.join(iconDir, '32x32.png'),
    path.join(iconDir, 'icon.ico')
  );
  console.log('Generated icon.ico');
  
  // Create .icns file (macOS) - just copy 128x128 for now
  fs.copyFileSync(
    path.join(iconDir, '128x128.png'),
    path.join(iconDir, 'icon.icns')
  );
  console.log('Generated icon.icns');
}

generateIcons().catch(console.error);