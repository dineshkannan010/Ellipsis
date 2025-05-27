import { useEffect, useState } from 'react';
import { HomePage } from './Screens/HomePage';
import { ContentGenerationView } from './Components/ContentGenerationView';

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [currentTitle, setCurrentTitle] = useState('');

  useEffect(() => {
    const storedView = sessionStorage.getItem('currentView');
    const storedTitle = sessionStorage.getItem('currentTitle');

    if (storedView === 'contentGeneration' && storedTitle) {
      setCurrentView('contentGeneration');
      setCurrentTitle(storedTitle);
    }

    window.addEventListener('beforeunload', () => sessionStorage.clear());

    return () => window.removeEventListener('beforeunload', () => sessionStorage.clear());
  }, []);

  return (
    <>
      {currentView === 'contentGeneration' ? (
        <div className="bg-gradient-to-b from-[#1f1f1f] to-[#121212] min-h-screen">
        <ContentGenerationView
          title={currentTitle}
          onBack={() => {
            setCurrentView('home');
            sessionStorage.clear();
          }}
        />
        </div>
      ) : (
        <HomePage
          onNavigate={(title) => {
            setCurrentView('contentGeneration');
            setCurrentTitle(title);
            sessionStorage.setItem('currentView', 'contentGeneration');
            sessionStorage.setItem('currentTitle', title);
          }}
        />
      )}
    </>
  );
}

export default App;

