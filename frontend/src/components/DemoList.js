import React from 'react';
import './DemoList.css';

const DemoList = ({ demos, onSelect }) => {
  const groupedDemos = demos.reduce((acc, demo) => {
    if (!acc[demo.category]) {
      acc[demo.category] = [];
    }
    acc[demo.category].push(demo);
    return acc;
  }, {});

  const categoryNames = {
    layer2: 'Layer 2 - Data Link',
    layer3: 'Layer 3 - Network',
    layer4: 'Layer 4 - Transport',
    application: 'Application Layer',
  };

  return (
    <div className="demo-list">
      <h2>Available Demos</h2>
      {Object.entries(groupedDemos).map(([category, categoryDemos]) => (
        <div key={category} className="demo-category">
          <h3>{categoryNames[category] || category}</h3>
          <div className="demo-grid">
            {categoryDemos.map((demo) => (
              <div
                key={demo.id}
                className="demo-card"
                onClick={() => onSelect(demo)}
              >
                <div className="demo-card-header">
                  <h4>{demo.name}</h4>
                  <span className={`badge ${demo.requires_root ? 'requires-root' : ''}`}>
                    {demo.requires_root ? '🔒 Root' : '✓ Safe'}
                  </span>
                </div>
                <p className="demo-description">{demo.description}</p>
                <div className="demo-meta">
                  <span>⏱️ Max {demo.max_runtime}s</span>
                  {demo.requires_network && <span>🌐 Network</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default DemoList;
