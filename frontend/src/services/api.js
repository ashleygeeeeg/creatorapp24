import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Showcase items
export const fetchShowcase = async () => {
  try {
    const response = await axios.get(`${API}/showcase`);
    return response.data.map(item => ({
      id: item.id,
      mobile: item.mobile_image,
      laptop: item.laptop_image,
    }));
  } catch (error) {
    console.error('Failed to fetch showcase:', error);
    return null;
  }
};

// Features
export const fetchFeatures = async () => {
  try {
    const response = await axios.get(`${API}/features`);
    return response.data.map(item => ({
      id: item.id,
      icon: item.icon,
      title: item.title,
      description: item.description,
      mockupType: item.mockup_type,
    }));
  } catch (error) {
    console.error('Failed to fetch features:', error);
    return null;
  }
};

// Stats
export const fetchStats = async () => {
  try {
    const response = await axios.get(`${API}/stats`);
    return {
      users: response.data.users_count,
      usersLabel: response.data.description,
    };
  } catch (error) {
    console.error('Failed to fetch stats:', error);
    return null;
  }
};

// Waitlist
export const joinWaitlist = async (email, name) => {
  const response = await axios.post(`${API}/waitlist`, { email, name });
  return response.data;
};

export const fetchWaitlistCount = async () => {
  try {
    const response = await axios.get(`${API}/waitlist/count`);
    return response.data.count;
  } catch (error) {
    console.error('Failed to fetch waitlist count:', error);
    return 0;
  }
};
