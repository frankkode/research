import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { User, AuthContextType, LoginCredentials, RegisterData } from '../types';
import { authApi } from '../services/api';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await authApi.login(credentials);
      const { token: newToken, user: newUser } = response.data;
      
      setToken(newToken);
      setUser(newUser);
      localStorage.setItem('token', newToken);
      localStorage.setItem('user', JSON.stringify(newUser));
    } catch (error) {
      throw error;
    }
  };

  const register = async (data: RegisterData) => {
    try {
      const response = await authApi.register(data);
      const { token: newToken, user: newUser } = response.data;
      
      setToken(newToken);
      setUser(newUser);
      localStorage.setItem('token', newToken);
      localStorage.setItem('user', JSON.stringify(newUser));
    } catch (error) {
      throw error;
    }
  };

  const googleAuth = async (token: string, studyGroup?: string) => {
    try {
      const response = await authApi.googleAuth(token, studyGroup);
      const { token: newToken, user: newUser } = response.data;
      
      setToken(newToken);
      setUser(newUser);
      localStorage.setItem('token', newToken);
      localStorage.setItem('user', JSON.stringify(newUser));
      
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    authApi.logout().catch(() => {});
  };

  const refreshUser = useCallback(async () => {
    try {
      console.log('Refreshing user data...');
      const response = await authApi.getProfile();
      const updatedUser = response.data;
      console.log('Updated user data received:', {
        consent_completed: updatedUser.consent_completed,
        pre_quiz_completed: updatedUser.pre_quiz_completed,
        interaction_completed: updatedUser.interaction_completed,
        post_quiz_completed: updatedUser.post_quiz_completed,
        study_group: updatedUser.study_group,
        participant_id: updatedUser.participant_id
      });
      
      // Create a new object to force React to re-render
      const newUser = { ...updatedUser };
      setUser(newUser);
      localStorage.setItem('user', JSON.stringify(newUser));
      console.log('User state updated successfully');
      
      // Return the updated user for immediate use
      return newUser;
    } catch (error) {
      console.error('Failed to refresh user data:', error);
      throw error;
    }
  }, []);

  const isAuthenticated = !!user && !!token;

  return (
    <AuthContext.Provider value={{ 
      user, 
      token, 
      login, 
      register, 
      googleAuth,
      logout, 
      refreshUser,
      isAuthenticated, 
      loading 
    }}>
      {children}
    </AuthContext.Provider>
  );
};