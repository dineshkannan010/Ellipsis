import axios from 'axios';

export const connectPlatform = async (platform: string) => {
  const response = await axios.post('/api/connect', { platform });
  return response.data;
};

export const disconnectPlatform = async (platform: string) => {
  const response = await axios.post('/api/disconnect', { platform });
  return response.data;
};

export const getConnectedPlatforms = async () => {
  const response = await axios.get('/api/connected_platforms');
  return response.data.connected_platforms;
};

export const fetchOAuthUrl = async (platform: string) => {
  const response = await axios.get(`/api/oauth_url/${platform}`);
  return response.data.oauth_url;
};