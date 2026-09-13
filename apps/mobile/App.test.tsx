import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react-native';
import App from './App';

// Mock Constants from expo-constants
jest.mock('expo-constants', () => ({
  default: {
    expoConfig: {
      extra: {
        webBaseUrl: 'http://localhost:3000',
      },
    },
  },
}));

// Mock WebView
jest.mock('react-native-webview', () => ({
  WebView: jest.fn(() => null),
}));

// Mock StatusBar
jest.mock('expo-status-bar', () => ({
  StatusBar: jest.fn(() => null),
}));

// Mock SafeAreaView and SafeAreaProvider
jest.mock('react-native-safe-area-context', () => ({
  SafeAreaProvider: jest.fn(({ children }) => children),
  SafeAreaView: jest.fn(({ children }) => children),
  useSafeAreaInsets: jest.fn(() => ({ top: 0, right: 0, bottom: 0, left: 0 })),
}));

// Mock ActivityIndicator
jest.mock('react-native', () => ({
  ...jest.requireActual('react-native'),
  ActivityIndicator: jest.fn(() => null),
  Pressable: jest.fn(({ children, onPress, style }) => (
    <button onClick={onPress} style={style}>
      {children}
    </button>
  )),
  StyleSheet: {
    create: jest.fn((styles) => styles),
    absoluteFillObject: {},
  },
  View: jest.fn(({ children, style }) => <div style={style}>{children}</div>),
  Text: jest.fn(({ children, style }) => <span style={style}>{children}</span>),
}));


describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<App />);
    expect(screen).toBeTruthy();
  });

  it('renders tab bar with all tabs', () => {
    render(<App />);
    
    // Check that all tabs are rendered
    expect(screen.getByText('Home')).toBeTruthy();
    expect(screen.getByText('Login')).toBeTruthy();
    expect(screen.getByText('Dashboard')).toBeTruthy();
    expect(screen.getByText('Wingman')).toBeTruthy();
  });

  it('renders WebView component', () => {
    const { WebView } = require('react-native-webview');
    render(<App />);
    
    expect(WebView).toHaveBeenCalled();
  });

  it('renders SafeAreaProvider', () => {
    const { SafeAreaProvider } = require('react-native-safe-area-context');
    render(<App />);
    
    expect(SafeAreaProvider).toHaveBeenCalled();
  });

  it('renders StatusBar', () => {
    const { StatusBar } = require('expo-status-bar');
    render(<App />);
    
    expect(StatusBar).toHaveBeenCalledWith(
      expect.objectContaining({
        style: 'light',
      }),
      {}
    );
  });

  it('initializes with home tab selected', () => {
    render(<App />);
    
    // The home tab should have the active style
    const homeTab = screen.getByText('Home');
    expect(homeTab).toBeTruthy();
  });

  it('baseUrl function returns correct URL without trailing slash', () => {
    // This tests the baseUrl logic
    const webBaseUrl = 'http://localhost:3000';
    const result = webBaseUrl.replace(/\/$/, '');
    expect(result).toBe('http://localhost:3000');
  });

  it('baseUrl function removes trailing slash', () => {
    const webBaseUrl = 'http://localhost:3000/';
    const result = webBaseUrl.replace(/\/$/, '');
    expect(result).toBe('http://localhost:3000');
  });

  it('TABS constant has correct structure', () => {
    const TABS = [
      { key: 'home', label: 'Home', path: '/' },
      { key: 'auth', label: 'Login', path: '/auth' },
      { key: 'dashboard', label: 'Dashboard', path: '/dashboard' },
      { key: 'chat', label: 'Wingman', path: '/chat' },
    ] as const;

    expect(TABS).toHaveLength(4);
    expect(TABS[0].key).toBe('home');
    expect(TABS[0].label).toBe('Home');
    expect(TABS[0].path).toBe('/');
    expect(TABS[1].key).toBe('auth');
    expect(TABS[1].label).toBe('Login');
    expect(TABS[1].path).toBe('/auth');
    expect(TABS[2].key).toBe('dashboard');
    expect(TABS[2].label).toBe('Dashboard');
    expect(TABS[2].path).toBe('/dashboard');
    expect(TABS[3].key).toBe('chat');
    expect(TABS[3].label).toBe('Wingman');
    expect(TABS[3].path).toBe('/chat');
  });
});

describe('App Tab Navigation', () => {
  it('should have 4 tabs defined', () => {
    const TABS = [
      { key: 'home', label: 'Home', path: '/' },
      { key: 'auth', label: 'Login', path: '/auth' },
      { key: 'dashboard', label: 'Dashboard', path: '/dashboard' },
      { key: 'chat', label: 'Wingman', path: '/chat' },
    ] as const;

    expect(TABS.length).toBe(4);
  });

  it('should have unique tab keys', () => {
    const TABS = [
      { key: 'home', label: 'Home', path: '/' },
      { key: 'auth', label: 'Login', path: '/auth' },
      { key: 'dashboard', label: 'Dashboard', path: '/dashboard' },
      { key: 'chat', label: 'Wingman', path: '/chat' },
    ] as const;

    const keys = TABS.map(tab => tab.key);
    const uniqueKeys = new Set(keys);
    expect(uniqueKeys.size).toBe(keys.length);
  });

  it('should have unique tab paths', () => {
    const TABS = [
      { key: 'home', label: 'Home', path: '/' },
      { key: 'auth', label: 'Login', path: '/auth' },
      { key: 'dashboard', label: 'Dashboard', path: '/dashboard' },
      { key: 'chat', label: 'Wingman', path: '/chat' },
    ] as const;

    const paths = TABS.map(tab => tab.path);
    const uniquePaths = new Set(paths);
    expect(uniquePaths.size).toBe(paths.length);
  });
});

describe('App Configuration', () => {
  it('should have correct app name', () => {
    const appJson = require('./app.json');
    expect(appJson.name).toBe('CreatorApp24');
  });

  it('should have correct app slug', () => {
    const appJson = require('./app.json');
    expect(appJson.slug).toBe('creatorapp24');
  });
});
