import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { LogOut, ShoppingCart } from 'lucide-react';
import { Outlet, Link } from 'react-router-dom';

interface LayoutProps {
  showHeader?: boolean;
}

const Layout: React.FC<LayoutProps> = ({ showHeader = true }) => {
  const { user, logOut } = useAuth();
  const navigate = useNavigate();

  const handleLogoClick = () => {
    navigate('/categories');
  };

  const handleLogout = async () => {
    try {
      await logOut();
      navigate('/login');
    } catch (error) {
      console.error('Failed to log out:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      {showHeader && (
        <header className="bg-black/50 backdrop-blur-md border-b border-gray-700/50 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div 
                className="flex items-center space-x-2 cursor-pointer hover:opacity-80 transition-opacity"
                onClick={handleLogoClick}
              >
                <ShoppingCart className="h-8 w-8 text-lavender-400" />
                <span className="text-2xl font-bold bg-gradient-to-r from-lavender-400 to-lavender-600 bg-clip-text text-transparent">
                  BestPickr
                </span>
              </div>
              
              {user && (
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <button 
                      onClick={() => navigate('/profile')}
                      className="flex items-center space-x-2 hover:opacity-80 transition-opacity"
                      title="View Profile"
                    >
                      <img 
                        src={user.photoURL || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.displayName || 'User')}&background=7e22ce&color=fff`} 
                        alt={user.displayName || 'User'}
                        className="w-8 h-8 rounded-full border-2 border-lavender-400"
                      />
                      <span className="text-white font-medium hidden sm:inline">{user.displayName || 'User'}</span>
                    </button>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="p-2 text-gray-400 hover:text-white transition-colors"
                    title="Logout"
                  >
                    <LogOut className="h-5 w-5" />
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>
      )}
      <main className="flex-1">
        <Outlet /> {/* Magic spot where child routes appear ✨ */}
      </main>
      <footer className="w-full bg-gray-900/95 border-t border-gray-700/70 py-10 mt-12 shadow-[0_-4px_24px_0_rgba(80,80,120,0.15)]">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-6">
            {/* Navigation Links */}
            <div className="space-y-3">
              <h3 className="text-lavender-400 font-semibold text-lg mb-4">Navigation</h3>
              <div className="space-y-2">
                <Link to="/" className="block text-gray-200 hover:text-lavender-400 transition-colors text-base">Home</Link>
                <Link to="/categories" className="block text-gray-200 hover:text-lavender-400 transition-colors text-base">Categories</Link>
                <Link to="/profile" className="block text-gray-200 hover:text-lavender-400 transition-colors text-base">Profile</Link>
                <a href="https://github.com/your-repo" target="_blank" rel="noopener noreferrer" className="block text-gray-200 hover:text-lavender-400 transition-colors text-base">About</a>
              </div>
            </div>

            {/* Contact Info */}
            <div className="space-y-3">
              <h3 className="text-lavender-400 font-semibold text-lg mb-4">Contact</h3>
              <div className="flex items-center gap-2 text-gray-300 text-base">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-lavender-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <a href="mailto:support@BestPickr.com" className="hover:text-lavender-400 underline font-medium">support@BestPickr.com</a>
              </div>
              <div className="text-gray-400 text-base">
                Made with <span className="text-lavender-400">♥</span> for smart shoppers
              </div>
            </div>

            {/* Description */}
            <div className="space-y-3">
              <h3 className="text-lavender-400 font-semibold text-lg mb-4">About BestPickr</h3>
              <div className="text-gray-400 text-base">
                BestPickr helps you compare prices, analyze products, and save money across rides, groceries, and e-commerce platforms. Your one-stop solution for smarter, thriftier shopping.
              </div>
            </div>
          </div>

          {/* Copyright */}
          <div className="border-t border-gray-700/50 pt-6 text-center">
            <span className="text-gray-400 text-sm">
              © {new Date().getFullYear()} <span className="font-semibold text-lavender-400">BestPickr</span>. All rights reserved.
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
