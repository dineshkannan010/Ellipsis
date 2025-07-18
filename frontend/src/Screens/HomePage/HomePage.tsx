import { ArrowRight, X, Plus, Loader2, MicIcon, Menu } from "lucide-react";
import React, { useState, KeyboardEvent, useEffect, useRef } from "react";
import { Button } from "@/Components/ui/button";
import { Card } from "@/Components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogTrigger,
  DialogTitle,
} from "@/Components/ui/dialog";
import { fetchTrendingTopics } from "@/services/trendingService";
import { ContentGenerationView } from "../../Components/ContentGenerationView";

import { connectPlatform, disconnectPlatform, getConnectedPlatforms, fetchOAuthUrl } from "@/services/socialService";

interface HomePageProps {
  onNavigate: (title: string) => void;
}

interface TrendingTopic {
  title: string;
  description: string;
  category: string;
}

// Data for category badges
interface Category {
  icon: string;
  label: string;
  alt: string;
  onClick?: () => void;
}

interface LoginStatus {
  [key: string]: {
    isConnected: boolean;
    lastChecked: number;
  }
}

export const HomePage = ({ onNavigate }: HomePageProps): JSX.Element => {
  const [postContent, setPostContent] = useState<string>("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [connectedPlatforms, setConnectedPlatforms] = useState<string[]>(() => {
    try {
      const stored = localStorage.getItem('connectedPlatforms');
      return stored ? JSON.parse(stored) : [];
    } catch (e) {
      console.error('Error reading connectedPlatforms from localStorage:', e);
      return [];
    }
  });
  const [isTrendingOpen,    setTrendingOpen]    = useState(false)
  const [trendingTopics,    setTrendingTopics]   = useState<TrendingTopic[]>([])
  const [isLoadingTrending, setLoadingTrending] = useState(false)
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [showContentGeneration, setShowContentGeneration] = useState(false);
  const [contentGenerationTitle, setContentGenerationTitle] = useState("");
  const [activeButtons, setActiveButtons] = useState<{
    trending: boolean;
    mic: boolean;
    arrow: boolean;
  }>({
    trending: false,
    mic: false,
    arrow: false,
  });
  const [isShareDialogOpen, setIsShareDialogOpen] = useState(false);
  const [platformDashboards, setPlatformDashboards] = useState<{[key: string]: string}>({});
  const [loginStatus, setLoginStatus] = useState<LoginStatus>(() => {
    try {
      const stored = localStorage.getItem('platformLoginStatus');
      return stored ? JSON.parse(stored) : {};
    } catch (e) {
      console.error('Error reading platformLoginStatus from localStorage:', e);
      return {};
    }
  });
  // Fix interval type and add abort controller
  const abortControllerRef = useRef<AbortController | null>(null);

  // Social media platforms
  const socialPlatforms = [
    {
      name: "Podbean",
      icon: "/Podbean.svg",
      className: "bg-[#313131] hover:bg-[#313131]/80",
      showInWelcome: false,
      url: "https://www.podbean.com/login",
      dashboardUrl: "https://www.podbean.com",
      checkLoginUrl: "https://www.podbean.com"
    },
    {
      name: "Spotify",
      icon: "/spotify.png",
      className: "bg-[#313131] hover:bg-[#313131]/80",
      showInWelcome: false,
      url: "https://podcasters.spotify.com/",
      dashboardUrl: "https://creators.spotify.com/pod/dashboard/home",
      checkLoginUrl: "https://creators.spotify.com/pod/dashboard"
    },
  ];

  const handleToggleSidebar = () => setSidebarOpen(!isSidebarOpen);

  const handleButtonClick = (buttonName: string) => {
    setActiveButtons(prev => ({
      ...prev,
      [buttonName]: !prev[buttonName as keyof typeof prev]
    }));
  };

  // Function to check if a platform is connected
  const isPlatformConnected = (platformName: string): boolean => {
    const status = loginStatus[platformName];
    if (!status) return false;
    
    // Consider connection stale after 5 minutes
    const STALE_THRESHOLD = 5 * 60 * 1000; // 5 minutes in milliseconds
    const now = Date.now();
    
    return status.isConnected && (now - status.lastChecked) < STALE_THRESHOLD;
  };

  // Function to update platform connection status
  const updatePlatformStatus = (platformName: string, isConnected: boolean) => {
    const newStatus: LoginStatus = {
      ...loginStatus,
      [platformName]: {
        isConnected,
        lastChecked: Date.now()
      }
    };
    
    setLoginStatus(newStatus);
    localStorage.setItem('platformLoginStatus', JSON.stringify(newStatus));

    // Update connected platforms list
    if (isConnected) {
      setConnectedPlatforms(prev => {
        if (!prev.includes(platformName)) {
          const newConnected = [...prev, platformName];
          localStorage.setItem('connectedPlatforms', JSON.stringify(newConnected));
          return newConnected;
        }
        return prev;
      });
    } else {
      setConnectedPlatforms(prev => {
        const newConnected = prev.filter(p => p !== platformName);
        localStorage.setItem('connectedPlatforms', JSON.stringify(newConnected));
        return newConnected;
      });
    }
  };

  async function onTrendingClick() {
    // If already open, just close
    if (isTrendingOpen) {
      return setTrendingOpen(false)
    }
  
    // otherwise open + fetch
    setTrendingOpen(true)
    setLoadingTrending(true)
    try {
      const topics = await fetchTrendingTopics()   // hits your new /api/trending
      setTrendingTopics(topics)
    } catch (err) {
      console.error("Failed to load trending:", err)
    } finally {
      setLoadingTrending(false)
    }
  }

  const handleConnect = (platformName: string) => {
    const platform = socialPlatforms.find(p => p.name === platformName);
    if (platform?.url) {
      const width = 600;
      const height = 700;
      const left = (window.innerWidth - width) / 2;
      const top = (window.innerHeight - height) / 2;
      
      const popup = window.open(
        platform.url,
        'Connect to ' + platformName,
        `width=${width},height=${height},left=${left},top=${top}`
      );

      if (!popup || popup.closed || typeof popup.closed === 'undefined') {
        alert('Please allow popups to connect with ' + platformName);
        return;
      }

      const checkPopup = setInterval(() => {
        if (!popup || popup.closed) {
          clearInterval(checkPopup);
          // Final check for successful connection
          verifyConnection(platformName);
          return;
        }

        try {
          const currentUrl = popup.location.href;
          if (isSuccessfulLoginUrl(platformName, currentUrl)) {
            clearInterval(checkPopup);
            handleSuccessfulConnection(platformName);
            popup.close();
          }
        } catch (error) {
          // Ignore cross-origin errors
        }
      }, 500);
    }
  };

  const isSuccessfulLoginUrl = (platformName: string, url: string): boolean => {
    switch (platformName) {
      case 'Spotify':
        return url.includes('creators.spotify.com/pod/dashboard') ||
               url.includes('podcasters.spotify.com/dashboard');
      case 'Podbean':
        return url.includes('podbean.com/dashboard') ||
               url.includes('podbean.com/user-');
      default:
        return false;
    }
  };

  const verifyConnection = async (platformName: string) => {
    const platform = socialPlatforms.find(p => p.name === platformName);
    if (!platform) return;

    try {
      // Try to access the dashboard URL
      const response = await fetch(platform.dashboardUrl, {
        method: 'HEAD',
        credentials: 'include'
      });

      updatePlatformStatus(platformName, response.ok);
      setIsDialogOpen(!response.ok);
    } catch (error) {
      console.error(`Failed to verify ${platformName} connection:`, error);
      updatePlatformStatus(platformName, false);
      setIsDialogOpen(true);
    }
  };

  const handleSuccessfulConnection = (platformName: string) => {
    console.log(`Handling successful connection for ${platformName}`);
    updatePlatformStatus(platformName, true);
    setIsDialogOpen(false);
  };

  const handleDisconnect = (platformName: string) => {
    console.log(`Disconnecting ${platformName}`);
    updatePlatformStatus(platformName, false);
    setIsDialogOpen(true);
  };

  // Check connection status periodically
  useEffect(() => {
    const checkConnections = () => {
      connectedPlatforms.forEach(platformName => {
        if (!isPlatformConnected(platformName)) {
          verifyConnection(platformName);
        }
      });
    };

    const interval = setInterval(checkConnections, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, [connectedPlatforms]);

  // Filter platforms based on connection status
  const visiblePlatforms = socialPlatforms.filter(
    (platform) => connectedPlatforms.includes(platform.name)
  );

  const unconnectedPlatforms = socialPlatforms.filter(
    (platform) => !connectedPlatforms.includes(platform.name)
  );

  // Update socialPlatforms with dashboard URLs
  const platformsWithDashboards = socialPlatforms.map(platform => ({
    ...platform,
    dashboardUrl: platformDashboards[platform.name] || undefined
  }));

  const handlePostContentKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && postContent.trim()) {
      e.preventDefault();
      setContentGenerationTitle(postContent);
      setShowContentGeneration(true);
    }
  };

  const handleTrendingTopicClick = (topic: TrendingTopic) => {
    setContentGenerationTitle(topic.title);
    setShowContentGeneration(true);
    setTrendingOpen(false);
  };


  // Save connected platforms to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('connectedPlatforms', JSON.stringify(connectedPlatforms));
  }, [connectedPlatforms]);

  if (showContentGeneration) {
    return (
      <div className="bg-gradient-to-b from-[#1f1f1f] to-[#121212] min-h-screen">
        <ContentGenerationView 
          title={contentGenerationTitle}
          onBack={() => setShowContentGeneration(false)}
          connectedPlatforms={connectedPlatforms}
          socialPlatforms={socialPlatforms}
          onConnect={handleConnect}
          isSidebarOpen={isSidebarOpen}
          onToggleSidebar={handleToggleSidebar}
        />
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-b from-[#1f1f1f] to-[#121212] flex justify-center items-center w-full min-h-screen">
      <div className="w-full max-w-[1280px] px-4 md:px-0 relative">
        {/* Sidebar */}
        <div
          className={`fixed left-0 top-0 h-screen transition-all duration-300 ease-in-out z-20
            ${isSidebarOpen ? "w-[153px] bg-[#121212]" : "w-[60px] bg-[#000000]"}`}
        >
          <div className={`flex flex-col ${isSidebarOpen ? "pt-12" : "pt-6"} px-4 ${isSidebarOpen ? "" : "items-center"}`}>
            <div className="flex flex-col gap-3">
              <button 
                onClick={handleToggleSidebar}
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

        {/* Sidebar Toggle Button - Only show in expanded state */}
        {isSidebarOpen && (
          <button
            className="fixed top-4 left-4 z-30 text-white"
            onClick={handleToggleSidebar}
          >
            <X className="w-6 h-6" />
          </button>
        )}

        {/* Main Content Area */}
        <div
          className={`flex flex-col items-center justify-center gap-6 pt-8 pb-12 transition-margin duration-300 ease-in-out
            ${isSidebarOpen ? "md:ml-[153px]" : "md:ml-[60px]"}`}
        >
          {/* Welcome Section */}
          <div className="text-center">
            <img src="/steppers.svg" alt="Steppers" className="mx-auto mb-6 w-[77px] h-[77px]" />
            <h1 className="font-['Inter'] font-medium text-xl md:text-2xl text-white">
              Welcome to <span className="text-[#9392e6]">Ellipsis</span>
            </h1>
          </div>

          {/* Description */}
          <p className="w-full md:w-[556px] font-['Inter'] text-sm text-[#a1a1a1] text-center">
            Ellipsis is an AI content assistant that writes, refines, and schedules posts, optimising tone, strategy, and timing to grow your online presence with ease.
          </p>

          {/* Connected Platforms and Connect Button Row */}
          <div className="flex flex-row items-center justify-center gap-4">
            {/* Connect Socials Button */}
            {unconnectedPlatforms.length > 0 && (
              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="flex items-center justify-center gap-2 w-[160px] h-[38px] rounded-[12px] bg-[#313131]/80 hover:bg-[#9388B3] hover:text-[#313131] transition-all duration-200 border-none text-[#a1a1a1]">
                    Connect Socials
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-[#1F1F1F] border border-[#313131] rounded-[24px] max-w-[600px] p-8">
                  <div className="flex flex-col items-center mb-16">
                    <h2 className="text-white text-2xl">Connect Your Socials</h2>
                  </div>
                  <div className="flex flex-row gap-4 justify-center">
                    {unconnectedPlatforms.map(platform => (
                      <button
                        key={platform.name}
                        onClick={() => handleConnect(platform.name)}
                        className="flex items-center justify-center gap-2 w-[160px] h-[38px] rounded-[12px] bg-[#313131]/80 hover:bg-[#9388B3] group transition-all duration-200"
                      >
                        <img src={platform.icon} alt={platform.name} className="w-5 h-5 opacity-80 group-hover:brightness-0" />
                        <span className="text-[#a1a1a1] text-base group-hover:text-[#313131]">{platform.name}</span>
                      </button>
                    ))}
                  </div>
                </DialogContent>
              </Dialog>
            )}

            {/* Connected Platform Buttons */}
            {visiblePlatforms.map(platform => (
              <button
                key={platform.name}
                onClick={() => window.open(platform.dashboardUrl, '_blank')}
                className="group relative flex items-center justify-center gap-2 w-[160px] h-[38px] rounded-[12px] bg-[#313131]/80 hover:bg-[#9388B3] transition-all duration-200"
              >
                <img src={platform.icon} alt={platform.name} className="w-5 h-5 opacity-80 group-hover:brightness-0" />
                <span className="text-[#a1a1a1] text-base group-hover:text-[#313131]">{platform.name}</span>
                
                {/* Disconnect button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDisconnect(platform.name);
                  }}
                  className="absolute right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                >
                  <X className="w-4 h-4 text-[#a1a1a1] hover:text-[#313131]" />
                </button>
              </button>
            ))}
          </div>

        {/* Post Creation Card */}
        <Card className="w-full max-w-[722px] bg-[#1f1f1f]/80 backdrop-blur-sm border border-[#313131] rounded-lg p-4 md:p-6">
          <textarea
            value={postContent}
            onChange={e => setPostContent(e.target.value)}
            onKeyDown={handlePostContentKeyPress}
            placeholder="Post About..."
            className="w-full bg-transparent resize-none text-[#a1a1a1] placeholder-[#a1a1a1] mb-4 outline-none"
          />

<div className="flex items-center gap-2">
    <button
      onClick={onTrendingClick}
      className={`px-3 py-1.5 rounded-lg flex items-center gap-2 group ${
        isTrendingOpen
          ? 'bg-[#9388B3] text-[#313131]'
          : 'bg-[#313131]/80 text-[#a1a1a1] hover:bg-[#9388B3] hover:text-[#313131]'
      }`}
    >
      <img 
        src="/trending-up.svg" 
        alt="Trending" 
        className={`w-4 h-4 transition-all duration-200 ${
          isTrendingOpen 
            ? 'brightness-0' 
            : 'opacity-80 group-hover:brightness-0'
        }`}
      />
      <span className="transition-colors duration-200">Trending</span>
    </button>

              <button
                onClick={() => {
                  handleButtonClick('arrow')
                  if (postContent.trim()) onNavigate(postContent)
                }}
                className={`ml-auto p-2 rounded-full transition-all duration-200 border border-transparent ${
                  activeButtons.arrow
                    ? 'bg-[#9388B3] text-[#313131]'
                    : 'bg-[#313131]/80 hover:bg-[#9388B3] hover:text-[#313131]'
                }`}
              >
                <ArrowRight
                  className={`w-4 h-4 transition-colors duration-200 ${
                    activeButtons.arrow ? 'text-[#313131]' : 'text-[#9388B3] hover:text-[#313131]'
                  }`}
                />
              </button>
            </div>

            {/* Trending Topics Display */}
            {isTrendingOpen && (
              <div className="mt-4 bg-[#1F1F1F] rounded-lg border border-[#313131] max-h-60 overflow-y-auto">
                {isLoadingTrending ? (
                  <div className="flex justify-center p-4">
                    <Loader2 className="animate-spin text-[#9392E6]" />
                  </div>
                ) : (
                  trendingTopics.map((t, i) => (
                    <div
                      key={i}
                      onClick={() => { handleTrendingTopicClick(t); handleButtonClick('trending'); }}
                      className="flex items-start px-4 py-3 hover:bg-[#9388B3] cursor-pointer transition"
                    >
                      <Plus className="w-4 h-4 text-[#a1a1a1] flex-shrink-0 mt-1" />
                      <div className="ml-3">
                        <div className="text-[#f8f8f8] font-medium text-sm">
                          {t.title}
                        </div>
                        <div className="mt-1 text-[#a1a1a1] text-xs leading-snug">
                          {t.description}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};
