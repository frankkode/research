import React, { useState } from 'react';
import SimpleAuthForm from '../components/auth/SimpleAuthForm';

const SimpleAuth: React.FC = () => {
  const [user, setUser] = useState<any>(null);

  const handleAuthSuccess = (userData: any) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
  };

  const testServer = async () => {
    try {
      const response = await fetch('http://localhost:8000/simple/test/');
      const data = await response.json();
      alert(`Server test: ${JSON.stringify(data)}`);
    } catch (error) {
      alert(`Server error: ${error}`);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Simple Authentication Test</h1>
      
      <button onClick={testServer} style={{ marginBottom: '20px', padding: '10px 20px' }}>
        Test Server Connection
      </button>

      {user ? (
        <div style={{ 
          maxWidth: '400px', 
          margin: '0 auto', 
          padding: '20px', 
          border: '2px solid green', 
          borderRadius: '8px',
          backgroundColor: '#f0fff0'
        }}>
          <h2>✅ Authentication Successful!</h2>
          <p><strong>Username:</strong> {user.username}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>Participant ID:</strong> {user.participant_id}</p>
          <p><strong>User ID:</strong> {user.id}</p>
          
          <button 
            onClick={handleLogout}
            style={{ 
              padding: '10px 20px', 
              backgroundColor: '#dc3545', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      ) : (
        <SimpleAuthForm onSuccess={handleAuthSuccess} />
      )}

      <div style={{ marginTop: '40px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
        <h3>Instructions:</h3>
        <ol>
          <li>Start Django server: <code>python manage.py runserver</code></li>
          <li>Click "Test Server Connection" to verify backend is running</li>
          <li>Register a new account or login with existing credentials</li>
          <li>This bypasses all CORS/Railway issues by using local Django server</li>
        </ol>
        
        <h3>Endpoints:</h3>
        <ul>
          <li><code>POST /simple/register/</code> - Register new user</li>
          <li><code>POST /simple/login/</code> - Login existing user</li>
          <li><code>GET /simple/test/</code> - Test server connection</li>
        </ul>
      </div>
    </div>
  );
};

export default SimpleAuth;