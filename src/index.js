import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import { SlotContextProvider } from './context/SlotContext';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <SlotContextProvider>
      <App />
    </SlotContextProvider>
  </React.StrictMode>
);
