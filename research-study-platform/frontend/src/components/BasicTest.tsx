import React from 'react';

const BasicTest = () => {
  console.log('BasicTest component is rendering!');
  
  React.useEffect(() => {
    console.log('BasicTest component mounted successfully!');
    document.title = 'Basic Test - Working';
  }, []);

  return (
    <div style={{ padding: '20px', border: '2px solid green', margin: '20px' }}>
      <h1 style={{ color: 'green' }}>✅ Basic Test Component</h1>
      <p>If you see this, React is working!</p>
      <p>Current time: {new Date().toLocaleTimeString()}</p>
      <button onClick={() => alert('Button works!')}>Test Button</button>
    </div>
  );
};

export default BasicTest;