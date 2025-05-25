interface TrendingTopic {
  title: string;
  description: string;
  category: string;
}

const SONAR_API_KEY = import.meta.env.VITE_SONAR_API_KEY || 'your_api_key_here';
const SONAR_ENDPOINT = 'https://api.perplexity.ai/sonar/trending';

export const fetchTrendingTopics = async (): Promise<TrendingTopic[]> => {
  try {
    const response = await fetch(SONAR_ENDPOINT, {
      headers: {
        'Authorization': `Bearer ${SONAR_API_KEY}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Failed to fetch trending topics');
    }

    const data = await response.json();
    
    // Transform Sonar API trending topics into our TrendingTopic format
    // Take only the top 5 trending topics
    return data.trends.slice(0, 5).map((trend: any) => ({
      title: trend.query,
      description: trend.summary || 'Trending topic',
      category: trend.category || 'General'
    }));

  } catch (error) {
    console.error('Error fetching trending topics:', error);
    // Return empty array in case of error to avoid breaking the UI
    return [];
  }
}; 