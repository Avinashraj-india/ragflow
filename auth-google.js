const { OAuth2Client } = require('google-auth-library');
const jwt = require('jsonwebtoken');

const client = new OAuth2Client(process.env.GOOGLE_CLIENT_ID);

async function verifyGoogleToken(req, res) {
  try {
    const { token } = req.body;
    const ticket = await client.verifyIdToken({
      idToken: token,
      audience: process.env.GOOGLE_CLIENT_ID,
    });
    
    const payload = ticket.getPayload();
    const { sub: googleId, email, name } = payload;
    
    // Generate your app token
    const appToken = jwt.sign(
      { googleId, email, name },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );
    
    res.json({ token: appToken, user: { email, name } });
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
}

module.exports = { verifyGoogleToken };