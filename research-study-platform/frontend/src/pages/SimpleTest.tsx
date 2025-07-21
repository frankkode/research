import React from 'react';

const SimpleTest: React.FC = () => {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Simple Test Page</h1>
      <p>If you can see this, the routing is working!</p>
      
      <button 
        onClick={() => alert('Button clicked!')}
        style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}
      >
        Test Button
      </button>
    </div>
  );
};

export default SimpleTest;