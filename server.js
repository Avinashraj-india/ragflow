const express = require('express');
const path = require('path');
const cors = require('cors');
const { verifyGoogleToken } = require('./auth-google');

const app = express();
app.use(cors({ origin: 'http://localhost:5173' }));
app.use(express.json());

// Google auth route
app.post('/auth/google', verifyGoogleToken);

// Callback route for popup
app.get('/auth/callback', (req, res) => {
  res.sendFile(path.join(__dirname, 'rag-ui/public/auth-callback.html'));
});

app.listen(8000, () => {
  console.log('Server running on port 8000');
});