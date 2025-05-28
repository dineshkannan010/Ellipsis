export async function fetchTrendingTopics() {
  const resp = await fetch('/api/trending');
  if (!resp.ok) throw new Error('Trending fetch failed');
  const { topics } = await resp.json();
  return topics as Array<{ title: string; description: string; category: string }>;
  }; 