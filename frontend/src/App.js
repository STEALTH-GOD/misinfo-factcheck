import React from "react";
import {BrowserRouter as Router, Routes, Route} from "react-router-dom";
import Navbar from "./components/Navbar";
import MisinformationDetector from "./components/MisinformationDetector";
import History from "./components/History";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="App min-h-screen bg-gray-50">
        <Navbar />
        <div className="pt-6">
          <Routes>
            <Route path="/" element={<MisinformationDetector />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
