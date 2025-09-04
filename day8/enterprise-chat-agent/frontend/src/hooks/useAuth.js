import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // Decode JWT to get user info
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const now = Date.now() / 1000;
        
        if (payload.exp > now) {
          setUser({
            user_id: payload.user_id,
            tenant_id: payload.tenant_id,
            roles: payload.roles
          });
          setIsAuthenticated(true);
          
          // Set default authorization header
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } else {
          localStorage.removeItem('access_token');
        }
      } catch (error) {
        console.error('Invalid token:', error);
        localStorage.removeItem('access_token');
      }
    }
    setLoading(false);
  }, []);

  const login = async (ssoToken) => {
    try {
      const response = await axios.post('/auth/login', {
        sso_token: ssoToken
      });

      const { access_token, user_info } = response.data;
      
      localStorage.setItem('access_token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      setUser(user_info);
      setIsAuthenticated(true);
      
      return user_info;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    setIsAuthenticated(false);
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
