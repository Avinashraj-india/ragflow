import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface GoogleSSOProps {
    buttonText?: string;
}

const GoogleSSO = ({ buttonText = 'Continue with Google' }: GoogleSSOProps) => {
    const navigate = useNavigate();

    useEffect(() => {
        if (window.google && import.meta.env.VITE_GOOGLE_CLIENT_ID) {
            window.google.accounts.id.initialize({
                client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
                callback: handleCredentialResponse,
            });

            window.google.accounts.id.renderButton(
                document.getElementById('google-signin-btn')!,
                { theme: 'outline', size: 'large', text: 'continue_with' }
            );
        }
    }, []);

    async function handleCredentialResponse(response: any) {
        try {
            const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/auth/google`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: response.credential })
            });
            
            if (res.ok) {
                const data = await res.json();
                localStorage.setItem('token', data.token);
                navigate('/chat');
            }
        } catch (error) {
            console.error('Google SSO failed:', error);
        }
    }

    return <div id="google-signin-btn"></div>;
};

export default GoogleSSO;
