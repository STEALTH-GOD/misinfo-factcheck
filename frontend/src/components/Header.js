import React from "react";

const Header = () => {
  return (
    <header className="text-center mb-12">
      <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
        AI Fact Checker
      </h1>
      <p className="text-xl text-white/90 max-w-2xl mx-auto">
        Verify claims using AI-powered analysis and trusted sources
      </p>
    </header>
  );
};

export default Header;
