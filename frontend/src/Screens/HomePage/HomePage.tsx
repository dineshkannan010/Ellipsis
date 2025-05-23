import { ArrowRight  , X, Plus, Loader2, MicIcon, Menu } from "lucide-react";
import React, { useState } from "react";
import { Badge } from "@/Components/ui/badge";
import { Button } from "@/Components/ui/button";
import { Card, CardContent } from "@/Components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogTrigger,
} from "@/Components/ui/dialog";
import { fetchTrendingTopics } from "@/services/trendingService";

interface TrendingTopic {
  title: string;
  description: string;
  category: string;
}

export const HomePage = (): JSX.Element => {
  const [postContent, setPostContent] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [connectedPlatforms, setConnectedPlatforms] = useState<string[]>([]);
  const [isTrendingModalOpen, setIsTrendingModalOpen] = useState(false);
  const [trendingTopics, setTrendingTopics] = useState<TrendingTopic[]>([]);
  const [isLoadingTopics, setIsLoadingTopics] = useState(false);
  const [expandedTopicIndex, setExpandedTopicIndex] = useState<number | null>(null);
  const [showTrendingTopics, setShowTrendingTopics] = useState(false);
  const [isSidebarOpen, setSidebarOpen] = useState(true);

  const handleToggleSidebar = () => setSidebarOpen(!isSidebarOpen);

  // Data for category badges
  const categories = [
    {
      icon: "/trending-up.svg",
      label: "Trending",
      alt: "Trending up",
      onClick: async () => {
        setShowTrendingTopics(!showTrendingTopics);
        if (!showTrendingTopics && trendingTopics.length === 0) {
          setIsLoadingTopics(true);
          try {
            const topics = await fetchTrendingTopics();
            setTrendingTopics(topics);
          } catch (error) {
            console.error("Failed to fetch trending topics:", error);
          } finally {
            setIsLoadingTopics(false);
          }
        }
      },
    },
    {
      icon: "/lightbulb-2.svg",
      label: "Opinion",
      alt: "Lightbulb",
    },
    {
      icon: "/takeout-dining.png",
      label: "Take Away",
      alt: "Takeout dining",
    },
    {
      icon: "/potted-plant.png",
      label: "Growth",
      alt: "Potted plant",
    },
  ];

  // Social media platforms
  const socialPlatforms = [
    {
      name: "LinkedIn",
      icon: "/linkedin.svg",
      className: "bg-[#313131] hover:bg-[#313131]/80",
    },
    {
      name: "Reddit",
      icon: "/reddit.svg",
      className: "bg-[#313131] hover:bg-[#313131]/80",
    },
    {
      name: "Twitter",
      icon: "/twitter.svg",
      className: "bg-[#313131] hover:bg-[#313131]/80",
    },
  ];

  const handleConnect = (platformName: string) => {
    setConnectedPlatforms((prev) => [...prev, platformName]);
  };

  const handleDisconnect = (platformName: string) => {
    setConnectedPlatforms((prev) => prev.filter((name) => name !== platformName));
  };

  const unconnectedPlatforms = socialPlatforms.filter(
    (platform) => !connectedPlatforms.includes(platform.name)
  );

  return (
  <div className="bg-gradient-to-b from-[#1f1f1f] to-[#121212] flex justify-center items-center w-full min-h-screen">
      <div className="w-full max-w-[1280px] px-4 md:px-0 relative">
        {/* Sidebar Toggle Button */}
        <button
          className="fixed top-4 left-4 z-30 text-white"
          onClick={handleToggleSidebar}
        >
          {isSidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>

        {/* Sidebar */}
        <div
  className={`fixed left-0 top-0 h-screen bg-[#121212] transition-transform duration-300 ease-in-out z-20
    ${isSidebarOpen ? "translate-x-0" : "-translate-x-full"} w-[153px]`}
>
  <div className="flex flex-col gap-6 pt-10 px-4">
    <div className="flex items-center justify-start gap-3 ">
      <img src="/steppers.svg" alt="Steppers" className="w-[45px] h-[45px]" />
      <span className="font-['Inter'] text-[14px] text-[#f8f8f8]">Ellipsis</span>
    </div>

    <div className="flex items-center justify-start gap-2 opacity-80">
      <img className="w-[20px] h-[20px]" alt="Finance mode" src="/finance-mode.png" />
      <span className="font-['Inter'] text-[12px] text-[#a0a0a0]">Performance</span>
    </div>
  </div>
</div>

        {/* Main Content Area */}
        <div
          className={`flex flex-col items-center justify-center gap-6 pt-24 pb-12 transition-margin duration-300 ease-in-out
            ${isSidebarOpen ? "md:ml-[153px]" : "md:ml-0"}`}
        >
        {/* Welcome Section */}
        <div className="text-center">
          <img src="/steppers.svg" alt="Steppers" className="mx-auto mb-8 w-[77px] h-[77px]" />
          <h1 className="font-['Inter'] font-medium text-xl md:text-2xl text-white">
            Welcome to <span className="text-[#9392e6]">Ellipsis</span>
          </h1>
        </div>

        {/* Description */}
        <p className="w-full md:w-[556px] font-['Inter'] text-sm text-[#a1a1a1] text-center">
          Ellipsis is an AI content assistant that writes, refines, and schedules posts, optimising tone, strategy, and timing to grow your online presence with ease.
        </p>

        {/* Connected Platforms */}
        {connectedPlatforms.length > 0 && (
          <div className="flex flex-wrap justify-center gap-4">
            {socialPlatforms
              .filter(platform => connectedPlatforms.includes(platform.name))
              .map(platform => (
                <button key={platform.name} onClick={() => handleDisconnect(platform.name)} className="flex items-center gap-2 px-3 py-1.5 bg-[#313131]/80 rounded-lg hover:bg-[#313131] transition">
                  <img src={platform.icon} alt={platform.name} className="w-5 h-5" />
                  <span className="text-[#a1a1a1] text-sm">{platform.name}</span>
                </button>
              ))}
          </div>
        )}

        {/* Connect Socials Button */}
        {unconnectedPlatforms.length > 0 && (
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-[#1F1F1F]/80 border border-[#313131] text-[#a1a1a1] rounded-lg px-5 py-2 hover:bg-[#313131] transition">
                Connect Socials
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#1F1F1F] border-[#313131] rounded-xl max-w-[400px]">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-white">Connect Your Socials</h2>
                <button onClick={() => setIsDialogOpen(false)} className="text-[#a1a1a1] hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>
              {unconnectedPlatforms.map(platform => (
                <button
                  key={platform.name}
                  onClick={() => handleConnect(platform.name)}
                  className={`flex items-center gap-3 px-4 py-2 rounded-lg text-[#a1a1a1] hover:bg-[#313131] transition ${platform.className}`}
                >
                  <img src={platform.icon} alt={platform.name} className="w-6 h-6" />
                  {platform.name}
                </button>
              ))}
            </DialogContent>
          </Dialog>
        )}

        {/* Post Creation Card */}
        <Card className="w-full max-w-[722px] bg-[#1f1f1f]/80 backdrop-blur-sm border border-[#313131] rounded-lg p-4 md:p-6">
          <textarea
            value={postContent}
            onChange={e => setPostContent(e.target.value)}
            placeholder="Post About..."
            className="w-full bg-transparent resize-none text-[#a1a1a1] placeholder-[#a1a1a1] mb-4 outline-none"
          />

          <div className="flex flex-wrap gap-2 md:gap-4 items-center">
            {categories.map((category, idx) => (
              <Badge key={idx} className="bg-[#313131]/80 text-[#a1a1a1] rounded-lg hover:bg-[#313131] transition cursor-pointer" onClick={category.onClick}>
                <img className="w-5 h-5 opacity-80" src={category.icon} alt={category.alt} />
                <span className="ml-1.5 text-xs whitespace-nowrap">{category.label}</span>
              </Badge>
            ))}

            <div className="flex items-center gap-2 ml-auto">
              <Button variant="ghost" className="bg-[#313131]/80 rounded-full hover:bg-[#313131] transition">
                <MicIcon className="w-4 h-4 text-[#9388B3]" />
              </Button>

              <Button variant="ghost" className="bg-[#313131]/80 rounded-full hover:bg-[#313131] transition">
                <ArrowRight className="w-4 h-4 text-[#9388B3]" />
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
);
};