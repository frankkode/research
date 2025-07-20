import React, { useEffect, useCallback } from 'react';

interface GoogleSignInProps {
  onSuccess: (token: string) => void;
  onError: (error: string) => void;
  text?: string;
}

declare global {
  interface Window {
    google: any;
  }
}

const GoogleSignIn: React.FC<GoogleSignInProps> = ({ onSuccess, onError, text = "Sign in with Google" }) => {
  const handleCredentialResponse = useCallback((response: any) => {
    console.log('Google credential response received:', response);
    if (response.credential) {
      onSuccess(response.credential);
    } else {
      onError('Failed to get Google credential');
    }
  }, [onSuccess, onError]);

  const initializeGoogle = useCallback(() => {
    if (!window.google?.accounts?.id) {
      console.error('Google Identity Services not available');
      onError('Google Sign-In not available');
      return;
    }

    const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;
    
    if (!clientId) {
      console.error('REACT_APP_GOOGLE_CLIENT_ID environment variable is not set');
      onError('Google Client ID not configured. Please check the setup guide.');
      return;
    }

    console.log('Initializing Google with client ID:', clientId.substring(0, 20) + '...');
    
    try {
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: handleCredentialResponse,
      });

      const buttonElement = document.getElementById('google-signin-button');
      if (buttonElement) {
        window.google.accounts.id.renderButton(buttonElement, {
          theme: 'outline',
          size: 'large',
          text: 'continue_with',
          width: '100%',
        });
      }
    } catch (error) {
      console.error('Error initializing Google Sign-In:', error);
      onError('Failed to initialize Google Sign-In');
    }
  }, [onError, handleCredentialResponse]);

  useEffect(() => {
    console.log('GoogleSignIn component mounted');
    
    // Check if already loaded
    if (window.google?.accounts?.id) {
      initializeGoogle();
      return;
    }
    
    // Load Google Identity Services script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);

    script.onload = () => {
      console.log('Google Identity Services script loaded');
      initializeGoogle();
    };

    script.onerror = () => {
      console.error('Failed to load Google Identity Services script');
      onError('Failed to load Google Sign-In');
    };

    return () => {
      // Cleanup script
      if (document.head.contains(script)) {
        document.head.removeChild(script);
      }
    };
  }, [onError, initializeGoogle]);

  return (
    <div className="w-full">
      <div id="google-signin-button" className="w-full flex justify-center"></div>
    </div>
  );
};

export default GoogleSignIn;