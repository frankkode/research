import React from 'react';

const InlineAuth = () => {
  const [username, setUsername] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [message, setMessage] = React.useState('');

  const testServer = async () => {
    try {
      const response = await fetch('http://localhost:8000/simple/test/');
      const data = await response.json();
      setMessage('✅ Server working: ' + JSON.stringify(data));
    } catch (error) {
      setMessage('❌ Server error: ' + String(error));
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('⏳ Logging in...');
    
    try {
      const response = await fetch('http://localhost:8000/simple/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setMessage('✅ Login successful! User: ' + JSON.stringify(data.user));
      } else {
        setMessage('❌ Login failed: ' + data.error);
      }
    } catch (error) {
      setMessage('❌ Network error: ' + String(error));
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>🚀 Simple Authentication Test</h1>
      
      <button 
        onClick={testServer}
        style={{ 
          padding: '10px 20px', 
          backgroundColor: '#28a745', 
          color: 'white', 
          border: 'none', 
          borderRadius: '4px',
          cursor: 'pointer',
          marginBottom: '20px'
        }}
      >
        Test Server
      </button>

      <form onSubmit={handleLogin} style={{ maxWidth: '300px', border: '1px solid #ccc', padding: '20px', borderRadius: '8px' }}>
        <h3>Login Form</h3>
        
        <div style={{ marginBottom: '10px' }}>
          <label>Username:</label>
          <input 
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{ width: '100%', padding: '8px', marginTop: '5px', border: '1px solid #ddd', borderRadius: '4px' }}
            placeholder="Enter username"
          />
        </div>

        <div style={{ marginBottom: '10px' }}>
          <label>Password:</label>
          <input 
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ width: '100%', padding: '8px', marginTop: '5px', border: '1px solid #ddd', borderRadius: '4px' }}
            placeholder="Enter password"
          />
        </div>

        <button 
          type="submit"
          style={{ 
            width: '100%', 
            padding: '10px', 
            backgroundColor: '#007bff', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Login
        </button>
      </form>

      {message && (
        <div style={{ 
          marginTop: '20px', 
          padding: '10px', 
          backgroundColor: message.includes('✅') ? '#d4edda' : '#f8d7da',
          border: `1px solid ${message.includes('✅') ? '#c3e6cb' : '#f5c6cb'}`,
          borderRadius: '4px',
          maxWidth: '500px'
        }}>
          {message}
        </div>
      )}

      <div style={{ marginTop: '30px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px', maxWidth: '500px' }}>
        <h4>Instructions:</h4>
        <ol>
          <li>Start Django: <code>python manage.py runserver</code></li>
          <li>Click "Test Server" to verify connection</li>
          <li>Try login with any username/password to test</li>
        </ol>
      </div>
    </div>
  );
};

export default InlineAuth;