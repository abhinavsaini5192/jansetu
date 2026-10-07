import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';
import { USER_ROLES } from '../config/constants';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [activeRole, setActiveRole] = useState("CITIZEN");
  const [isLoading, setIsLoading] = useState(true);

  // Initialize session on mount
  useEffect(() => {
    const initAuth = async () => {
      setIsLoading(true);
      try {
        const stored = authService.getStoredSession();
        if (stored.token) {
          setToken(stored.token);
          const currentUser = await authService.getCurrentUser();
          if (currentUser) {
            setUser(currentUser);
            setActiveRole(currentUser.role || "CITIZEN");
          } else if (stored.user) {
            setUser(stored.user);
            setActiveRole(stored.user.role || "CITIZEN");
          }
        }
      } catch (err) {
        console.warn("Auth session initialization skipped or offline:", err.message);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (credentials) => {
    setIsLoading(true);
    try {
      const data = await authService.login(credentials);
      setUser(data.user);
      setToken(data.token);
      setActiveRole(data.user?.role || "CITIZEN");
      return data;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await authService.logout();
      setUser(null);
      setToken(null);
      setActiveRole("CITIZEN");
    } finally {
      setIsLoading(false);
    }
  };

  // Switch role function allows switching views in system without hardcoding identity
  const switchRole = (roleId) => {
    setActiveRole(roleId);
    if (user) {
      setUser(prev => ({ ...prev, role: roleId }));
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      isAuthenticated: Boolean(token && user),
      activeRole,
      switchRole,
      roles: USER_ROLES,
      isLoading,
      login,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
