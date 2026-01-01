import React from 'react';
import './MainLayout.css';

export const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="main-layout">
      {/* Sidebar could go here in a future iteration */}
      <main className="main-content">
        {children}
      </main>
    </div>
  );
};
