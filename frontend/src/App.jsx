import React from 'react';
import SlotGenerator from './components/SlotGenerator';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Office Booking System</h1>
      </header>
      <main>
        <SlotGenerator />
      </main>
      <footer>
        <p>&copy; 2023 Office Booking System</p>
      </footer>
    </div>
  );
}

export default App;
