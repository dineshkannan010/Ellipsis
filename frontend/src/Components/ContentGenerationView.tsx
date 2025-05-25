import React, { useState, useEffect } from 'react';
import { Play, Download, Share2, ArrowRight, MicIcon, X } from 'lucide-react';
import { Badge } from "@/Components/ui/badge";
import { Button } from "@/Components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogTitle,
} from "@/Components/ui/dialog";

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
  connectedPlatforms: string[];
  socialPlatforms: {
    name: string;
    icon: string;
    className: string;
    showInWelcome: boolean;
    url: string;
    dashboardUrl?: string;
  }[];
  onConnect: (platformName: string) => void;
  isSidebarOpen: boolean;
  onToggleSidebar: () => void;
}

export const ContentGenerationView: React.FC<ContentGenerationViewProps> = ({ 
  title, 
  onBack,
  connectedPlatforms,
  socialPlatforms,
  onConnect,
  isSidebarOpen,
  onToggleSidebar,
}) => {
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
  const [isShareDialogOpen, setIsShareDialogOpen] = useState(false);

  const handleButtonClick = (buttonName: string) => {
    setActiveButtons(prev => ({
      ...prev,
      [buttonName]: !prev[buttonName as keyof typeof prev]
    }));
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsContentVisible(false);
      setTimeout(() => {
        setCurrentStep((prev) => (prev + 1) % agentSteps.length);
        setIsContentVisible(true);
      }, 200);
    }, agentSteps[currentStep].duration);

    const responseTimer = setTimeout(() => {
      setResponseGenerated(true);
      setIsLoading(false);
    }, 12000);

    // Animate the dots
    const dotTimer = setInterval(() => {
      setActiveDot((prev) => (prev + 1) % 3);
    }, 400);

    return () => {
      clearTimeout(timer);
      clearTimeout(responseTimer);
      clearInterval(dotTimer);
    };
  }, [currentStep]);

  const CurrentIcon = agentSteps[currentStep].icon;

  const LoadingDots = () => (
    <div className="flex items-center gap-1 ml-3 relative top-[1px]">
      {[0, 1, 2].map((index) => (
        <div
          key={index}
          className={`w-2.5 h-2.5 rounded-full border-2 border-[#9392E6] ${
            activeDot === index ? 'bg-[#9392E6]' : ''
          } transition-colors duration-200`}
        />
      ))}
    </div>
  );

  const handleShareClick = (platformName: string) => {
    const platform = socialPlatforms.find(p => p.name === platformName);
    if (!platform) return;

    if (connectedPlatforms.includes(platformName)) {
      // If connected, go to dashboard if URL exists
      if (platform.dashboardUrl) {
        window.open(platform.dashboardUrl, "_blank");
      } else {
        // Fallback to default URLs if dashboard URL not set
        const defaultUrls: { [key: string]: string } = {
          "Podbean": "https://www.podbean.com/login",
          "Spotify": "https://creators.spotify.com/pod/dashboard/home"
        };
        window.open(defaultUrls[platformName], "_blank");
      }
    } else {
      // If not connected, go to login page
      window.open(platform.url, "_blank");
      onConnect(platformName);
    }
    setIsShareDialogOpen(false);
  };

  return (
    <>
      {/* Sidebar Toggle Button - Only show in expanded state */}
      {isSidebarOpen && (
        <button
          className="fixed top-4 left-4 z-30 text-white"
          onClick={onToggleSidebar}
        >
          <X className="w-6 h-6" />
        </button>
      )}

      {/* Sidebar */}
      <div
        className={`fixed left-0 top-0 h-screen transition-all duration-300 ease-in-out z-20
          ${isSidebarOpen ? "w-[153px] bg-[#121212]" : "w-[60px] bg-[#000000]"}`}
      >
        <div className={`flex flex-col ${isSidebarOpen ? "pt-12" : "pt-6"} px-4 ${isSidebarOpen ? "" : "items-center"}`}>
          <div className="flex flex-col gap-3">
            <button 
              onClick={onToggleSidebar}
              className="flex items-center gap-2 cursor-pointer"
            >
              <img 
                src="/steppers.svg" 
                alt="Steppers" 
                className={`${isSidebarOpen ? "w-[45px] h-[45px]" : "w-[35px] h-[35px]"}`}
              />
              {isSidebarOpen && (
                <span className="font-['Inter'] text-[14px] text-[#f8f8f8]">Ellipsis</span>
              )}
            </button>

            {isSidebarOpen && (
              <div className="flex items-center gap-2 opacity-80">
                <img className="w-[20px] h-[20px]" alt="Finance mode" src="/finance-mode.png" />
                <span className="font-['Inter'] text-[12px] text-[#a0a0a0]">Performance</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className={`transition-margin duration-300 ease-in-out ${isSidebarOpen ? "ml-[153px]" : "ml-[60px]"}`}>
        <div className="w-full max-w-[900px] mx-auto p-8">
          {/* Title */}
          <h1 className="text-white text-2xl mb-6">{title}</h1>

          {/* Agent Generating Content Box */}
          <div className="bg-[#2E2D2D] rounded-xl py-4 mb-6">
            <div className="flex justify-center items-center text-[#A1A1A1] text-sm">
              <div className="flex items-center">
                Agent generating content
                {isLoading && <LoadingDots />}
              </div>
            </div>
          </div>

          {/* Response Grid Container */}
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div className="bg-[#1F1F1F] border border-[#313131] rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-[#A1A1A1] text-sm">Response 1</span>
                <span className="text-[#A1A1A1] text-xs opacity-60">Artificial</span>
              </div>
              <div className="h-[200px]"></div>
            </div>
            <div className="bg-[#1F1F1F] border border-[#313131] rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-[#A1A1A1] text-sm">Response 2</span>
                <span className="text-[#A1A1A1] text-xs opacity-60">Artificial</span>
              </div>
              <div className="h-[200px]"></div>
            </div>
          </div>

          {/* Agent Status Box */}
          <div className="bg-[#2E2D2D] rounded-xl py-4 mb-6">
            <div className="flex justify-center items-center text-[#A1A1A1] text-sm">
              <div className="flex items-center">
                <div className="text-[#9392E6] mr-2">
                  <CurrentIcon />
                </div>
                {agentSteps[currentStep].name}
                <span className="ml-2">working on the content</span>
                {!responseGenerated && <LoadingDots />}
              </div>
            </div>
          </div>

          {/* Script Ready Text */}
          <div className="text-[#A1A1A1] text-sm mb-4">Your script is ready!</div>

          {/* Audio Player */}
          <div className="bg-[#2E2D2D] rounded-xl py-3 px-6 mb-6">
            <div className="flex items-center gap-4">
              <button 
                className={`p-1.5 bg-transparent border-2 border-[#9493E7] rounded-full transition-colors ${
                  activeButtons.play ? 'bg-[#9493E7]/20' : 'hover:bg-[#9493E7]/10'
                }`}
                onClick={() => {
                  setActiveButtons(prev => ({ ...prev, play: !prev.play }));
                  setIsPlaying(!isPlaying);
                }}
              >
                <Play className="w-3.5 h-3.5 text-[#9493E7]" fill="currentColor" />
              </button>
              <div className="flex-1 h-1 bg-[#313131] rounded-full relative">
                <div 
                  className="absolute left-0 top-0 h-full bg-[#9493E7] rounded-full transition-all duration-200"
                  style={{ width: '30%' }}
                >
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3.5 h-3.5 rounded-full bg-[#9493E7]"></div>
                </div>
              </div>
              <span className="text-[#A1A1A1] text-xs">00:00/3:00</span>
              <div className="flex items-center gap-2">
                <button 
                  className="p-2 rounded-full transition-all duration-200 border border-transparent bg-[#313131]/80 hover:bg-[#9388B3] group"
                >
                  <Download className="w-4 h-4 text-[#9388B3] group-hover:text-[#313131] transition-colors duration-200" />
                </button>
                <Dialog open={isShareDialogOpen} onOpenChange={setIsShareDialogOpen}>
                  <button 
                    onClick={() => setIsShareDialogOpen(true)}
                    className="px-4 py-1.5 bg-[#313131]/80 border border-transparent rounded-lg hover:bg-[#9388B3] transition-all duration-200 group"
                  >
                    <span className="text-[#A1A1A1] text-xs group-hover:text-[#313131]">Share</span>
                  </button>
                  <DialogContent className="bg-[#1F1F1F] border border-[#313131] rounded-[24px] max-w-[600px] p-8">
                    <DialogTitle className="text-white text-2xl text-center mb-8">Share To</DialogTitle>
                    <div className="flex flex-row gap-4 justify-center">
                      {socialPlatforms.map(platform => (
                        <button
                          key={platform.name}
                          onClick={() => handleShareClick(platform.name)}
                          className="flex items-center justify-center gap-2 w-[160px] h-[38px] rounded-[12px] bg-[#313131]/80 hover:bg-[#9388B3] group transition-all duration-200"
                        >
                          <img src={platform.icon} alt={platform.name} className="w-5 h-5 opacity-80 group-hover:brightness-0" />
                          <span className="text-[#a1a1a1] text-base group-hover:text-[#313131]">
                            {platform.name}
                          </span>
                        </button>
                      ))}
                    </div>
                    <button 
                      onClick={() => setIsShareDialogOpen(false)} 
                      className="absolute right-5 top-5 text-white/40 hover:bg-[#9388B3] hover:text-[#313131] p-2 rounded-full transition-all duration-200"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </DialogContent>
                </Dialog>
              </div>
            </div>
          </div>

          {/* Script Box */}
          <div className="bg-[#1F1F1F] border border-[#313131] rounded-xl p-4 mb-48">
            <div className="flex items-center justify-between mb-3">
              <span className="text-[#A1A1A1] text-sm">Generated Script</span>
              <button className="px-4 py-1.5 bg-[#313131]/80 border border-transparent rounded-lg hover:bg-[#9388B3] transition-all duration-200 group">
                <span className="text-[#A1A1A1] text-xs group-hover:text-[#313131]">Edit</span>
              </button>
            </div>
            <div className="text-[#A1A1A1] text-sm min-h-[200px] whitespace-pre-wrap"></div>
          </div>
        </div>
      </div>

      {/* Post About Box - Sticky */}
      <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-[#121212] via-[#121212]/90 to-transparent pt-32">
        <div className={`transition-margin duration-300 ease-in-out ${isSidebarOpen ? "ml-[153px]" : "ml-[60px]"}`}>
          <div className="w-full max-w-[900px] mx-auto p-8">
            <div className="bg-[#1f1f1f]/90 backdrop-blur-lg border border-[#313131] rounded-lg p-4">
              <textarea
                placeholder="Post About..."
                className="w-full bg-transparent resize-none text-[#a1a1a1] placeholder-[#a1a1a1] mb-4 outline-none focus:ring-1 focus:ring-[#9493E7] rounded"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleButtonClick('arrow');
                    setTimeout(() => handleButtonClick('arrow'), 200);
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
                    onClick={() => handleButtonClick('arrow')}
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
    </>
  );
}; 