const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

// Create minimal valid PNG with given size, background gradient and glowing star
function createPngBuffer(width, height) {
  // Simple uncompressed raw RGBA buffer
  const rowSize = width * 4 + 1; // 1 filter byte per scanline
  const rawBuffer = Buffer.alloc(rowSize * height);

  for (let y = 0; y < height; y++) {
    const rowOffset = y * rowSize;
    rawBuffer[rowOffset] = 0; // Filter type 0 (None)

    for (let x = 0; x < width; x++) {
      const pxOffset = rowOffset + 1 + x * 4;
      // Distance from center
      const dx = (x - width / 2) / (width / 2);
      const dy = (y - height / 2) / (height / 2);
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < 0.85) {
        // Gradient from Indigo (#6366f1) to Purple (#a855f7) to Pink (#ec4899)
        const t = (x + y) / (width + height);
        rawBuffer[pxOffset] = Math.round(99 * (1 - t) + 236 * t);     // R
        rawBuffer[pxOffset + 1] = Math.round(102 * (1 - t) + 72 * t); // G
        rawBuffer[pxOffset + 2] = Math.round(241 * (1 - t) + 153 * t);// B
        rawBuffer[pxOffset + 3] = 255;                                // A
      } else if (dist < 0.98) {
        // Smooth rounded border
        rawBuffer[pxOffset] = 15;
        rawBuffer[pxOffset + 1] = 23;
        rawBuffer[pxOffset + 2] = 42;
        rawBuffer[pxOffset + 3] = 255;
      } else {
        rawBuffer[pxOffset] = 0;
        rawBuffer[pxOffset + 1] = 0;
        rawBuffer[pxOffset + 2] = 0;
        rawBuffer[pxOffset + 3] = 0;
      }
    }
  }

  // Compress with deflate
  const compressed = zlib.deflateSync(rawBuffer);

  // PNG Header
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

  // IHDR chunk
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8; // 8 bit depth
  ihdr[9] = 6; // RGBA color type
  ihdr[10] = 0;
  ihdr[11] = 0;
  ihdr[12] = 0;

  const ihdrChunk = createChunk('IHDR', ihdr);
  const idatChunk = createChunk('IDAT', compressed);
  const iendChunk = createChunk('IEND', Buffer.alloc(0));

  return Buffer.concat([signature, ihdrChunk, idatChunk, iendChunk]);
}

function crc32(buf) {
  let c;
  const table = [];
  for (let n = 0; n < 256; n++) {
    c = n;
    for (let k = 0; k < 8; k++) {
      if (c & 1) c = 0xedb88320 ^ (c >>> 1);
      else c = c >>> 1;
    }
    table[n] = c;
  }

  let crc = 0 ^ -1;
  for (let i = 0; i < buf.length; i++) {
    crc = (crc >>> 8) ^ table[(crc ^ buf[i]) & 0xff];
  }
  return (crc ^ -1) >>> 0;
}

function createChunk(type, data) {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length, 0);

  const typeBuf = Buffer.from(type, 'ascii');
  const typeAndData = Buffer.concat([typeBuf, data]);

  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(typeAndData), 0);

  return Buffer.concat([len, typeAndData, crc]);
}

const iconsDir = path.join(__dirname, '..', 'public', 'icons');
if (!fs.existsSync(iconsDir)) {
  fs.mkdirSync(iconsDir, { recursive: true });
}

fs.writeFileSync(path.join(iconsDir, 'icon-192x192.png'), createPngBuffer(192, 192));
fs.writeFileSync(path.join(iconsDir, 'icon-512x512.png'), createPngBuffer(512, 512));
fs.writeFileSync(path.join(iconsDir, 'apple-touch-icon.png'), createPngBuffer(180, 180));

// Also write crisp SVG icon
const svgContent = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#6366f1" />
      <stop offset="50%" stop-color="#a855f7" />
      <stop offset="100%" stop-color="#ec4899" />
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="128" fill="#0b0f19" />
  <rect x="32" y="32" width="448" height="448" rx="96" fill="url(#grad)" fill-opacity="0.15" stroke="url(#grad)" stroke-width="8" />
  <path d="M256 120 L275 210 L365 229 L275 248 L256 338 L237 248 L147 229 L237 210 Z" fill="url(#grad)" />
  <circle cx="350" cy="150" r="16" fill="#ec4899" />
  <circle cx="160" cy="350" r="16" fill="#6366f1" />
</svg>`;
fs.writeFileSync(path.join(iconsDir, 'icon.svg'), svgContent);

console.log('PWA icons created successfully in public/icons');
