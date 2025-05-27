import React, { useState, useEffect, useMemo } from 'react';
import { Play, Download, Share2, ArrowRight, MicIcon } from 'lucide-react';
import Markdown from 'react-markdown';
import { usePodcastSSE } from '../hooks/usePodcastSSE'

const CritiqueIcon = () => (
  <img src="/public/edit.svg" alt="edit" className="w-5 h-5" />
);

const ContentStrategyIcon = () => (
  <img src="/public/bid_landscape.svg" alt="bid landscape" className="w-5 h-5" />
);

const StorytellerIcon = () => (
  <img src="/public/book_ribbon.svg" alt="book ribbon" className="w-5 h-5" />
);

const PublicReviewIcon = () => (
  <img src="/public/contacts_product.svg" alt="contacts product" className="w-5 h-5" />
);

interface AgentStep {
  icon: React.FC;
  name: string;
  duration: number;
}

const agentSteps: AgentStep[] = [
  { icon: CritiqueIcon, name: 'Critique Agent', duration: 3000 },
  { icon: ContentStrategyIcon, name: 'Content Strategy Agent', duration: 2500 },
  { icon: StorytellerIcon, name: 'Storyteller Agent', duration: 2000 },
  { icon: PublicReviewIcon, name: 'Public Review Agent', duration: 2500 },
];

interface ContentGenerationViewProps {
  title: string;
  onBack?: () => void;
}

type Stage =
  | 'crawling'
  | 'initialResponses'
  | 'debate'
  | 'scriptReady'
  | 'audioGenerating'
  | 'audioError'
  | 'audioReady';

export const ContentGenerationView: React.FC<ContentGenerationViewProps> = ({ title, onBack }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isContentVisible, setIsContentVisible] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [responseGenerated, setResponseGenerated] = useState(false);
  const [activeDot, setActiveDot] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeButtons, setActiveButtons] = useState({
    play: false,
    download: false,
    share: false,
    mic: false,
    arrow: false,
    trending: false,
    opinion: false,
    takeAway: false,
    growth: false,
  });
  
  // bottom input for next round
  const [nextPrompt, setNextPrompt] = useState<string>('');

  // State for podcast generation
  const [stage, setStage] = useState<Stage>('crawling');
  const [responses, setResponses] = useState<{ general_public?: string; critic?: string }>({});
  const [script, setScript] = useState<string>('');
  const [audioSrc, setAudioSrc] = useState<string>('');


  // manual SSE hookup
  usePodcastSSE({ setStage, setResponses, setScript, setAudioSrc });


  const handleButtonClick = (buttonName: string) => {
    setActiveButtons(prev => ({
      ...prev,
      [buttonName]: !prev[buttonName as keyof typeof prev]
    }));
  };

  // helper to submit next prompt
  const canSubmitNext = stage === 'audioReady';
  const handleNextSubmit = () => {
    if (!canSubmitNext || !nextPrompt.trim()) return;
    // reset runner state
    setStage('crawling');
    setResponses({});
    setScript('');
    setAudioSrc('');
    setCurrentStep(0);

    // fire next job
    fetch('http://localhost:5000/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: nextPrompt }),
    }).catch(console.error);

    setNextPrompt('');
  };



  // Kick off the job
  useEffect(() => {
    fetch('http://localhost:5000/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: title })
    }).catch(console.error);
  }, [title]);

  // Animate the loading dots
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveDot(d => (d + 1) % 3);
    }, 400);
    return () => clearInterval(interval);
  }, []);

  const LoadingDots = () => (
    <div className="flex items-center gap-1 ml-3">
      {[0, 1, 2].map(i => (
        <div
          key={i}
          className={`w-2 h-2 rounded-full border-2 border-[#9392E6] ${
            activeDot === i ? 'bg-[#9392E6]' : ''
          }`}
        />
      ))}
    </div>
  );
  
  // Header text per stage
  const headerText = {
    crawling: 'Agent generating content',
    initialResponses: 'Initial responses ready – Agents working on content',
    debate: 'Debating & synthesizing content',
    scriptReady: 'Final script ready – Generating audio',
    audioGenerating: 'Audio file is getting generated',
    audioError: 'Audio generation failed',
    audioReady: 'Podcast generated!'
  }[stage];

  return (
    <div className="w-full max-w-[900px] mx-auto p-8">
      <div className="pb-[150px] md:pb-[180px]"> 
      {/* Title */}
      <h1 className="text-white text-2xl mb-6">{title}</h1>

      {/* Stage Header */}
      <div className="bg-[#2E2D2D] rounded-xl py-4 mb-6">
        <div className="flex justify-center items-center text-[#A1A1A1] text-sm">
          <div className="flex items-center">
            {headerText}
            {stage !== 'audioReady' && <LoadingDots />}
          </div>
        </div>
      </div>

      {/* 2 Initial Responses */}
      {['initialResponses', 'debate', 'scriptReady', 'audioGenerating','audioError', 'audioReady'].includes(stage) &&
        responses.general_public &&
        responses.critic && (
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div className="bg-[#1F1F1F] border border-[#313131] rounded-xl p-4">
              <span className="text-[#A1A1A1] text-sm">Response 1</span>
              <div className="text-gray-300 mt-2">
                <Markdown>{responses.general_public}</Markdown>
              </div>
            </div>
            <div className="bg-[#1F1F1F] border border-[#313131] rounded-xl p-4">
              <span className="text-[#A1A1A1] text-sm">Response 2</span>
              <div className="text-gray-300 mt-2">
                <Markdown>{responses.critic}</Markdown>
              </div>
            </div>
          </div>
      )}

      {/* Final Script */}
      {['scriptReady', 'audioGenerating','audioError', 'audioReady'].includes(stage) && script && (
        <div className="bg-[#1F1F1F] rounded-xl p-4 mb-6">
          <span className="text-[#A1A1A1] text-sm">Generated Script</span>
          <div className="text-gray-300 mt-2">
            <Markdown>{script}</Markdown>
          </div>
        </div>
      )}

      {/* Audio Player */}
      {stage === 'audioReady' && audioSrc ? (
        <div className="bg-[#2E2D2D] rounded-xl py-3 px-6 mb-6">
          <audio controls className="w-full">
            <source src={audioSrc} type="audio/wav" />
            Your browser does not support the audio element.
          </audio>
          <div className="mt-2 text-[#A1A1A1] text-center">Podcast generated!</div>
        </div>
      ) : null}
      </div>

      {/* Agent Steps */}
      
      {/* Post About Box - Sticky */}
      <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-[#121212] via-[#121212]/90 to-transparent pt-32">
        <div className="w-full max-w-[900px] mx-auto px-8">
          <div className="bg-[#1f1f1f]/90 backdrop-blur-lg border border-[#313131] rounded-lg p-4">
            <textarea
              value={nextPrompt}
              onChange={e => setNextPrompt(e.target.value)}
              placeholder="Post About..."
              className="w-full bg-transparent resize-none text-[#a1a1a1] placeholder-[#a1a1a1] mb-4 outline-none focus:ring-1 focus:ring-[#9493E7] rounded"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleNextSubmit();
                }
              }}
            />

            <div className="flex flex-wrap gap-2 md:gap-4 items-center">
              <button 
                onClick={() => handleButtonClick('trending')}
                className={`flex items-center px-3 py-1.5 rounded-lg transition-all duration-200 border border-transparent group ${
                  activeButtons.trending 
                    ? 'bg-[#9388B3] text-[#313131]' 
                    : 'bg-[#313131]/80 text-[#a1a1a1] hover:bg-[#9388B3] hover:text-[#313131]'
                }`}
              >
                <img 
                  className={`w-5 h-5 transition-opacity duration-200 ${
                    activeButtons.trending 
                      ? 'brightness-0' 
                      : 'opacity-80 group-hover:brightness-0'
                  }`} 
                  src="/trending-up.svg" 
                  alt="Trending up" 
                />
                <span className="ml-1.5 text-xs whitespace-nowrap">Trending</span>
              </button>

              <button 
                onClick={() => handleButtonClick('opinion')}
                className={`flex items-center px-3 py-1.5 rounded-lg transition-all duration-200 border border-transparent group ${
                  activeButtons.opinion 
                    ? 'bg-[#9388B3] text-[#313131]' 
                    : 'bg-[#313131]/80 text-[#a1a1a1] hover:bg-[#9388B3] hover:text-[#313131]'
                }`}
              >
                <img 
                  className={`w-5 h-5 transition-opacity duration-200 ${
                    activeButtons.opinion 
                      ? 'brightness-0' 
                      : 'opacity-80 group-hover:brightness-0'
                  }`} 
                  src="/lightbulb-2.svg" 
                  alt="Lightbulb" 
                />
                <span className="ml-1.5 text-xs whitespace-nowrap">Opinion</span>
              </button>

              <button 
                onClick={() => handleButtonClick('takeAway')}
                className={`flex items-center px-3 py-1.5 rounded-lg transition-all duration-200 border border-transparent group ${
                  activeButtons.takeAway 
                    ? 'bg-[#9388B3] text-[#313131]' 
                    : 'bg-[#313131]/80 text-[#a1a1a1] hover:bg-[#9388B3] hover:text-[#313131]'
                }`}
              >
                <img 
                  className={`w-5 h-5 transition-opacity duration-200 ${
                    activeButtons.takeAway 
                      ? 'brightness-0' 
                      : 'opacity-80 group-hover:brightness-0'
                  }`} 
                  src="/takeout-dining.png" 
                  alt="Takeout dining" 
                />
                <span className="ml-1.5 text-xs whitespace-nowrap">Take Away</span>
              </button>

              <button 
                onClick={() => handleButtonClick('growth')}
                className={`flex items-center px-3 py-1.5 rounded-lg transition-all duration-200 border border-transparent group ${
                  activeButtons.growth 
                    ? 'bg-[#9388B3] text-[#313131]' 
                    : 'bg-[#313131]/80 text-[#a1a1a1] hover:bg-[#9388B3] hover:text-[#313131]'
                }`}
              >
                <img 
                  className={`w-5 h-5 transition-opacity duration-200 ${
                    activeButtons.growth 
                      ? 'brightness-0' 
                      : 'opacity-80 group-hover:brightness-0'
                  }`} 
                  src="/potted-plant.png" 
                  alt="Potted plant" 
                />
                <span className="ml-1.5 text-xs whitespace-nowrap">Growth</span>
              </button>

              <div className="flex items-center gap-2 ml-auto">
                <button 
                  onClick={() => handleButtonClick('mic')}
                  className={`p-2 rounded-full transition-all duration-200 border border-transparent group ${
                    activeButtons.mic 
                      ? 'bg-[#9388B3]' 
                      : 'bg-[#313131]/80 hover:bg-[#9388B3]'
                  }`}
                >
                  <MicIcon className={`w-4 h-4 transition-colors duration-200 ${
                    activeButtons.mic ? 'text-[#313131]' : 'text-[#9388B3] group-hover:text-[#313131]'
                  }`} />
                </button>

                <button 
                  onClick={handleNextSubmit}
                  disabled={!canSubmitNext}
                  className={`p-2 rounded-full transition-all duration-200 border border-transparent ${
                    activeButtons.arrow 
                      ? 'bg-[#9388B3] text-[#313131]' 
                      : 'bg-[#313131]/80 hover:bg-[#9388B3] hover:text-[#313131]'
                  }`}
                >
                  <ArrowRight className={`w-4 h-4 transition-colors duration-200 ${
                    activeButtons.arrow ? 'text-[#313131]' : 'text-[#9388B3] hover:text-[#313131]'
                  }`} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 