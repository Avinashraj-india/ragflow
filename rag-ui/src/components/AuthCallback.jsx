import { useEffect } from 'react';

const AuthCallback = () => {
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    
    if (code) {
      // Send success message to parent window
      window.opener?.postMessage({
        type: 'GOOGLE_AUTH_SUCCESS',
        code: code,
        user: { email: 'user@example.com' } // You'd normally exchange code for user info
      }, window.location.origin);
      
      // Close popup
      window.close();
    } else {
      // Handle error
      window.opener?.postMessage({
        type: 'GOOGLE_AUTH_ERROR',
        error: 'No authorization code received'
      }, window.location.origin);
      
      window.close();
    }
  }, []);

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <p>Processing Google authentication...</p>
    </div>
  );
};

export default AuthCallback;