interface TrendingTopic {
  title: string;
  description: string;
  category: string;
}

const mockTrendingTopics: TrendingTopic[] = [
  {
    title: "AI in Healthcare",
    description: "Latest developments in AI-driven medical diagnostics",
    category: "Technology"
  },
  {
    title: "Sustainable Energy",
    description: "Breakthroughs in renewable energy solutions",
    category: "Environment"
  },
  {
    title: "Digital Privacy",
    description: "New regulations and their impact on user data protection",
    category: "Technology"
  },
  {
    title: "Remote Work Culture",
    description: "Evolving workplace trends and best practices",
    category: "Business"
  }
];

export const fetchTrendingTopics = async (): Promise<TrendingTopic[]> => {
  // TODO: Replace with actual API call when API key is properly configured
  // For now, return mock data
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(mockTrendingTopics);
    }, 1000);
  });
}; 