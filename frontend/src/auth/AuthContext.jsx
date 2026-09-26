import { createContext, useContext, useState, useEffect } from 'react';
import { setTokenProvider } from '../api/client';
import {
  CognitoUser,
  AuthenticationDetails,
  CognitoUserAttribute,
} from 'amazon-cognito-identity-js';
import { userPool } from './cognitoConfig';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  setTokenProvider(getValidIdToken);
  const [currentUser, setCurrentUser] = useState(null);
  const [idToken, setIdToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // On app load, check if there's already a valid session (e.g., page refresh)
  useEffect(() => {
    const cognitoUser = userPool.getCurrentUser();
    if (!cognitoUser) {
      setLoading(false);
      return;
    }

    cognitoUser.getSession((err, session) => {
      if (err || !session.isValid()) {
        setLoading(false);
        return;
      }
      setIdToken(session.getIdToken().getJwtToken());
      setCurrentUser({
        sub: session.getIdToken().payload.sub,
        email: session.getIdToken().payload.email,
      });
      setLoading(false);
    });
  }, []);

  function register(email, password) {
    return new Promise((resolve, reject) => {
      const attributeList = [
        new CognitoUserAttribute({ Name: 'email', Value: email }),
      ];
      userPool.signUp(email, password, attributeList, null, (err, result) => {
        if (err) {
          reject(err);
          return;
        }
        resolve(result);
      });
    });
  }

  function confirmRegistration(email, code) {
    return new Promise((resolve, reject) => {
      const cognitoUser = new CognitoUser({ Username: email, Pool: userPool });
      cognitoUser.confirmRegistration(code, true, (err, result) => {
        if (err) {
          reject(err);
          return;
        }
        resolve(result);
      });
    });
  }

  function login(email, password) {
    return new Promise((resolve, reject) => {
      const authDetails = new AuthenticationDetails({
        Username: email,
        Password: password,
      });
      const cognitoUser = new CognitoUser({ Username: email, Pool: userPool });

      cognitoUser.authenticateUser(authDetails, {
        onSuccess: (session) => {
          const token = session.getIdToken().getJwtToken();
          setIdToken(token);
          setCurrentUser({
            sub: session.getIdToken().payload.sub,
            email: session.getIdToken().payload.email,
          });
          resolve(session);
        },
        onFailure: (err) => {
          reject(err);
        },
      });
    });
  }

  function logout() {
    const cognitoUser = userPool.getCurrentUser();
    if (cognitoUser) {
      cognitoUser.signOut();
    }
    setCurrentUser(null);
    setIdToken(null);
  }

  // Called by the API client before each request to ensure a fresh token
  function getValidIdToken() {
    return new Promise((resolve, reject) => {
      const cognitoUser = userPool.getCurrentUser();
      if (!cognitoUser) {
        reject(new Error('Not authenticated'));
        return;
      }
      cognitoUser.getSession((err, session) => {
        if (err || !session.isValid()) {
          reject(err || new Error('Session invalid'));
          return;
        }
        // getSession() automatically refreshes an expired IdToken
        // using the stored RefreshToken under the hood.
        const token = session.getIdToken().getJwtToken();
        setIdToken(token);
        resolve(token);
      });
    });
  }

  const value = {
    currentUser,
    idToken,
    loading,
    register,
    confirmRegistration,
    login,
    logout,
    getValidIdToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}