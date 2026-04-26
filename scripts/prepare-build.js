const fs = require('fs');
const path = require('path');

function prepare() {
  const source = path.join(__dirname, '../frontend/out');
  const destination = path.join(__dirname, '../build');

  // Remove destination if it exists
  if (fs.existsSync(destination)) {
    fs.rmSync(destination, { recursive: true, force: true });
  }
  
  // Check if source exists
  if (fs.existsSync(source)) {
    fs.renameSync(source, destination);
    console.log('Build folder prepared successfully.');
  } else {
    console.error('Source "frontend/out" not found. Make sure "npm run build" in frontend succeeded.');
    process.exit(1);
  }
}

try {
  prepare();
} catch (err) {
  console.error('Error preparing build folder:', err);
  process.exit(1);
}
