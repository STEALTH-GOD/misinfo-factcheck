import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Search, History, Shield } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="bg-white shadow-lg border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <Shield className="h-8 w-8 text-navy-600" style={{color: '#1e3a8a'}} />
              <span 
                className="text-2xl font-bold tracking-tight"
                style={{color: '#1e3a8a'}}
              >
                MisInfoDetectAI
              </span>
            </Link>
          </div>

          {/* Navigation Links */}
          <div className="flex items-center space-x-8">
            <Link
              to="/"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/') 
                  ? 'bg-navy-100 text-navy-700' 
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
              }`}
              style={isActive('/') ? {backgroundColor: '#dbeafe', color: '#1e3a8a'} : {}}
            >
              <Search className="h-4 w-4" />
              <span>Fact Check</span>
            </Link>

            <Link
              to="/history"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/history') 
                  ? 'bg-navy-100 text-navy-700' 
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
              }`}
              style={isActive('/history') ? {backgroundColor: '#dbeafe', color: '#1e3a8a'} : {}}
            >
              <History className="h-4 w-4" />
              <span>History</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;