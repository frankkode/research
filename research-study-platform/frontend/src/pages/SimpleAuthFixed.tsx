import React, { useState } from 'react';

const SimpleAuthFixed: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState<any>(null);

  const testServer = async () => {
    try {
      const response = await fetch('http://localhost:8000/simple/test/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      setMessage(`✅ Server test successful: ${data.message}`);
    } catch (error) {
      setMessage(`❌ Server error: ${error}`);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const endpoint = isLogin ? '/simple/login/' : '/simple/register/';
      const body = isLogin 
        ? { username: formData.username, password: formData.password }
        : { username: formData.username, email: formData.email, password: formData.password };

      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
      });

      const data = await response.json();

      if (data.success) {
        setMessage(`✅ ${data.message}`);
        setUser(data.user);
      } else {
        setMessage(`❌ ${data.error}`);
      }
    } catch (error) {
      setMessage(`❌ Network error: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleLogout = () => {
    setUser(null);
    setMessage('');
    setFormData({ username: '', email: '', password: '' });
  };

  if (user) {
    return (
      <div style={{ padding: '20px' }}>
        <div style={{ 
          maxWidth: '500px', 
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
              cursor: 'pointer',
              marginTop: '10px'
            }}
          >
            Logout & Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Simple Authentication System</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={testServer} 
          style={{ 
            padding: '10px 20px', 
            backgroundColor: '#28a745', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          🔧 Test Server Connection
        </button>
      </div>

      <div style={{ maxWidth: '400px', margin: '0 auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
        <h2>{isLogin ? '🔐 Login' : '📝 Register'}</h2>
        
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Username:</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              required
              style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
              placeholder="Enter your username"
            />
          </div>

          {!isLogin && (
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>Email:</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
                placeholder="Enter your email"
              />
            </div>
          )}

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Password:</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
              placeholder="Enter your password"
            />
          </div>

          <button 
            type="submit" 
            disabled={loading}
            style={{ 
              width: '100%', 
              padding: '12px', 
              backgroundColor: loading ? '#ccc' : '#007bff', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '16px'
            }}
          >
            {loading ? '⏳ Processing...' : (isLogin ? '🚀 Login' : '✅ Register')}
          </button>
        </form>

        <div style={{ textAlign: 'center', margin: '20px 0' }}>
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button 
            onClick={() => {
              setIsLogin(!isLogin);
              setMessage('');
              setFormData({ username: '', email: '', password: '' });
            }}
            style={{ 
              background: 'none', 
              border: 'none', 
              color: '#007bff', 
              cursor: 'pointer', 
              textDecoration: 'underline',
              fontSize: '16px'
            }}
          >
            {isLogin ? '📝 Register here' : '🔐 Login here'}
          </button>
        </div>
      </div>

      {message && (
        <div style={{ 
          maxWidth: '400px',
          margin: '20px auto',
          padding: '15px', 
          backgroundColor: message.includes('✅') ? '#d4edda' : '#f8d7da',
          border: `1px solid ${message.includes('✅') ? '#c3e6cb' : '#f5c6cb'}`,
          borderRadius: '6px',
          textAlign: 'center'
        }}>
          {message}
        </div>
      )}

      <div style={{ marginTop: '40px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px', maxWidth: '600px', margin: '40px auto 0' }}>
        <h3>📋 Instructions:</h3>
        <ol>
          <li><strong>Start Django server:</strong> <code>python manage.py runserver</code></li>
          <li><strong>Click "Test Server Connection"</strong> to verify backend is running</li>
          <li><strong>Register a new account</strong> or login with existing credentials</li>
          <li><strong>Success!</strong> This bypasses all CORS/Railway issues</li>
        </ol>
        
        <h3>🔗 Endpoints:</h3>
        <ul>
          <li><code>GET /simple/test/</code> - Test server connection</li>
          <li><code>POST /simple/register/</code> - Register new user</li>
          <li><code>POST /simple/login/</code> - Login existing user</li>
        </ul>
      </div>
    </div>
  );
};

export default SimpleAuthFixed;