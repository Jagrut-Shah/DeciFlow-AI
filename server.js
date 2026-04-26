const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 8080;

// Serve static files from the 'build' directory
app.use(express.static(path.join(__dirname, 'build')));

// Handle API requests or other backend logic here
// For now, we'll just serve the frontend
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', service: 'DeciFlow AI Node Server' });
});

// The "catchall" handler: for any request that doesn't
// match one above, send back React's index.html file.
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server is listening on port ${PORT}`);
});
