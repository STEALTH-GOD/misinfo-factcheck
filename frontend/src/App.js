import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import HomePage from "./components/HomePage";
import ArticleDetailPage from "./pages/ArticleDetailPage";
import MisinformationDetector from "./components/MisinformationDetector";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/detector" element={<MisinformationDetector />} />
          <Route path="/article/:articleId" element={<ArticleDetailPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;