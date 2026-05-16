import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { BookOpen, Home, MessageSquare, User, Menu, X, LogOut } from 'lucide-react';
import { useAppStore } from '../store';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { isAuthenticated, user, logout } = useAppStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center space-x-2">
            <BookOpen className="w-8 h-8 text-indigo-600" />
            <span className="text-xl font-bold text-gray-900">语言学习平台</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-gray-700 hover:text-indigo-600 transition-colors font-medium">
              <Home className="w-5 h-5 inline mr-1" />
              首页
            </Link>
            <Link to="/courses" className="text-gray-700 hover:text-indigo-600 transition-colors font-medium">
              <BookOpen className="w-5 h-5 inline mr-1" />
              课程
            </Link>
            <Link to="/community" className="text-gray-700 hover:text-indigo-600 transition-colors font-medium">
              <MessageSquare className="w-5 h-5 inline mr-1" />
              社区
            </Link>
            <Link to="/progress" className="text-gray-700 hover:text-indigo-600 transition-colors font-medium">
              <User className="w-5 h-5 inline mr-1" />
              进度
            </Link>
            {isAuthenticated && (
              <Link to="/profile" className="text-gray-700 hover:text-indigo-600 transition-colors font-medium">
                <User className="w-5 h-5 inline mr-1" />
                个人中心
              </Link>
            )}
          </div>

          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold">
                  {user?.name.charAt(0).toUpperCase()}
                </div>
                <span className="text-gray-700 font-medium">{user?.name}</span>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 text-gray-600 hover:text-red-600 transition-colors"
                >
                  <LogOut className="w-5 h-5" />
                  <span>退出</span>
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Link
                  to="/login"
                  className="text-gray-700 hover:text-indigo-600 transition-colors font-medium"
                >
                  登录
                </Link>
                <Link
                  to="/register"
                  className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors font-medium"
                >
                  注册
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100"
          >
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className="md:hidden bg-white border-t">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 space-y-3">
            <Link
              to="/"
              onClick={() => setIsMenuOpen(false)}
              className="block py-2 text-gray-700 hover:text-indigo-600 transition-colors font-medium"
            >
              首页
            </Link>
            <Link
              to="/courses"
              onClick={() => setIsMenuOpen(false)}
              className="block py-2 text-gray-700 hover:text-indigo-600 transition-colors font-medium"
            >
              课程
            </Link>
            <Link
              to="/community"
              onClick={() => setIsMenuOpen(false)}
              className="block py-2 text-gray-700 hover:text-indigo-600 transition-colors font-medium"
            >
              社区
            </Link>
            <Link
              to="/progress"
              onClick={() => setIsMenuOpen(false)}
              className="block py-2 text-gray-700 hover:text-indigo-600 transition-colors font-medium"
            >
              进度
            </Link>
            {isAuthenticated && (
              <Link
                to="/profile"
                onClick={() => setIsMenuOpen(false)}
                className="block py-2 text-gray-700 hover:text-indigo-600 transition-colors font-medium"
              >
                个人中心
              </Link>
            )}
            <div className="pt-4 border-t">
              {isAuthenticated ? (
                <div className="mb-4 flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold">
                    {user?.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{user?.name}</p>
                    <p className="text-sm text-gray-500">{user?.email}</p>
                  </div>
                </div>
              ) : null}
              {isAuthenticated ? (
                <button
                  onClick={() => {
                    handleLogout();
                    setIsMenuOpen(false);
                  }}
                  className="w-full text-left py-2 text-red-600 hover:text-red-700 transition-colors font-medium"
                >
                  退出登录
                </button>
              ) : (
                <div className="space-y-3">
                  <Link
                    to="/login"
                    onClick={() => setIsMenuOpen(false)}
                    className="block py-2 text-gray-700 hover:text-indigo-600 transition-colors font-medium"
                  >
                    登录
                  </Link>
                  <Link
                    to="/register"
                    onClick={() => setIsMenuOpen(false)}
                    className="block w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors font-medium text-center"
                  >
                    注册
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
