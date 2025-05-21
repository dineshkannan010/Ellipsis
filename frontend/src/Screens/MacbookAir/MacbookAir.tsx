import { MicIcon, X, Plus, Loader2 } from "lucide-react";
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

export const MacbookAir = (): JSX.Element => {
  const [postContent, setPostContent] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [connectedPlatforms, setConnectedPlatforms] = useState<string[]>([]);
  const [isTrendingModalOpen, setIsTrendingModalOpen] = useState(false);
  const [trendingTopics, setTrendingTopics] = useState<TrendingTopic[]>([]);
  const [isLoadingTopics, setIsLoadingTopics] = useState(false);
  const [expandedTopicIndex, setExpandedTopicIndex] = useState<number | null>(null);
  const [showTrendingTopics, setShowTrendingTopics] = useState(false);

  // Mock topics for demonstration
  const topics = [
    "AI in the Workplace",
    "AI in the Workplace",
    "AI in the Workplace",
    "AI in the Workplace"
  ];

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
    <div className="bg-gradient-to-b from-[#1f1f1f] to-[#121212] flex flex-row justify-center w-full min-h-screen">
      <div className="w-full max-w-[1280px] h-[832px] relative px-4 md:px-0">
        {/* Sidebar */}
        <div className="hidden md:block absolute w-[153px] h-[889px] top-[-29px] left-0 bg-[#121212]">
          {/* Logo and App Name */}
          <div className="flex w-[117px] items-center absolute top-8 left-[9px] gap-[11px]">
            {/* Steppers SVG Logo */}
            <img
              src="/steppers.svg"
              alt="Steppers"
              className="w-[77px] h-[77px]"
            />
            <div className="font-['Inter'] text-[14px] text-[#f8f8f8] ml-1">
              Ellipsis
            </div>
          </div>

          {/* Sidebar Navigation Item */}
          <div className="flex w-[107px] items-center absolute top-[131px] left-[19px] gap-3">
            <img
              className="w-[22.12px] h-[22.12px] opacity-60"
              alt="Finance mode"
              src="/finance-mode.png"
            />
            <div className="font-['Inter'] text-xs text-[#a0a0a0]">
              Performance
            </div>
          </div>
        </div>

        {/* Mobile Header */}
        <div className="flex md:hidden items-center justify-between p-4 bg-[#121212]">
          <div className="flex items-center gap-[11px]">
            {/* Steppers SVG Logo for Mobile */}
            <img
              src="/steppers.svg"
              alt="Steppers"
              className="w-[77px] h-[77px]"
            />
            <div className="font-['Inter'] text-[14px] text-[#f8f8f8] ml-1">
              Ellipsis
            </div>
          </div>
        </div>

        {/* Welcome Section */}
        <div className="absolute w-full md:w-[402px] left-0 md:left-[449px] top-[182px] text-center px-4 md:px-0">
          {/* Loading Dots */}
          <img
            src="/steppers.svg"
            alt="Steppers"
            className="mx-auto mb-[36px] w-[77px] h-[77px]"
          />
          
          <h1 className="font-['Inter'] font-medium text-xl md:text-2xl leading-[29px] text-white mb-[44px]">
            Welcome to <span className="text-[#9392e6]">Ellipsis</span>
          </h1>
        </div>

        {/* Description */}
        <p className="absolute w-full md:w-[556px] top-[324px] left-0 md:left-[344px] font-['Inter'] text-[13px] text-[#a1a1a1] text-center leading-[18px] px-4 md:px-0">
          Ellipsis is an AI content assistant that writes, refines, and
          schedules posts, optimising tone, strategy, and timing to grow your
          online presence with ease.
        </p>

        {/* Post Creation Card */}
        <div className="absolute w-full md:w-[722px] top-[461px] left-0 md:left-[289px] px-4 md:px-0">
          {/* Glow effect */}
          <div className="absolute w-full h-[176px] bg-[rgba(87,86,227,0.15)] rounded-[5px] blur-[119px]" />

          <Card className="w-full md:w-[722px] bg-[#1f1f1f]/80 backdrop-blur-sm rounded-[15px] border border-solid border-[#313131]">
            <CardContent className="p-4 md:p-6">
              {/* Text input area */}
              <textarea
                value={postContent}
                onChange={(e) => setPostContent(e.target.value)}
                placeholder="Post About..."
                className="w-full bg-transparent border-none outline-none resize-none font-['Inter'] text-base text-[#a1a1a1] focus:ring-0 placeholder:text-[#a1a1a1] mb-4"
              />

              {/* Category badges */}
              <div className="flex flex-wrap gap-2 md:gap-[25px] mb-4">
                {categories.map((category, index) => (
                  <Badge
                    key={index}
                    className={`flex h-[22.28px] items-center px-[6.96px] py-0 ${
                      category.label === "Trending" && showTrendingTopics
                        ? "bg-[#9392e6]/20 text-[#9392e6]"
                        : "bg-[#313131]/80"
                    } backdrop-blur-sm rounded-[6.96px] hover:bg-[#313131] transition-colors cursor-pointer`}
                    onClick={category.onClick}
                  >
                    <img
                      className="w-[22.28px] h-[22.28px] opacity-80"
                      alt={category.alt}
                      src={category.icon}
                    />
                    <span className="ml-1.5 font-['Inter'] text-[11.1px] text-[#a1a1a1] whitespace-nowrap">
                      {category.label}
                    </span>
                  </Badge>
                ))}

                {/* MicIcon button */}
                <Button
                  variant="ghost"
                  className="flex w-[31px] h-[31px] p-[5px] bg-[#313131]/80 rounded-[57px] items-center justify-center hover:bg-[#313131] ml-auto"
                >
                  <MicIcon className="w-[14px] h-[19px] text-[#9388B3]" />
                </Button>
              </div>

              {/* Trending Topics */}
              {showTrendingTopics && (
                <div className="space-y-2">
                  {isLoadingTopics ? (
                    <div className="flex items-center justify-center p-4">
                      <Loader2 className="w-6 h-6 text-[#9392e6] animate-spin" />
                    </div>
                  ) : (
                    trendingTopics.map((topic, index) => (
                      <div
                        key={index}
                        onClick={() => setExpandedTopicIndex(expandedTopicIndex === index ? null : index)}
                        className="flex items-start gap-3 p-3 bg-[#313131]/50 rounded-lg cursor-pointer hover:bg-[#313131]/60 transition-colors"
                      >
                        <Plus
                          className={`w-4 h-4 text-[#a1a1a1] transition-transform mt-1 ${
                            expandedTopicIndex === index ? 'rotate-45' : ''
                          }`}
                        />
                        <div className="flex-1">
                          <span className="text-[#a1a1a1] text-sm font-['Inter'] block">{topic.title}</span>
                          {expandedTopicIndex === index && (
                            <p className="text-[#a1a1a1]/80 text-xs mt-2">{topic.description}</p>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Connected Platforms */}
        {connectedPlatforms.length > 0 && (
          <div className="absolute w-full md:w-auto top-[380px] left-0 md:left-[449px] flex justify-center gap-4 mb-4">
            {socialPlatforms
              .filter((platform) => connectedPlatforms.includes(platform.name))
              .map((platform) => (
                <button
                  key={platform.name}
                  onClick={() => handleDisconnect(platform.name)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#313131]/80 hover:bg-[#313131] transition-colors"
                >
                  <img
                    src={platform.icon}
                    alt={platform.name}
                    className="w-5 h-5"
                  />
                  <span className="text-[#a1a1a1] text-sm">{platform.name}</span>
                </button>
              ))}
          </div>
        )}

        {/* Connect Socials Dialog */}
        {unconnectedPlatforms.length > 0 && (
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button
                variant="outline"
                className="absolute h-8 px-5 py-0 top-[396px] left-1/2 transform -translate-x-1/2 md:left-[542px] md:transform-none bg-[#1F1F1F]/80 backdrop-blur-sm border border-[#313131] text-[#a1a1a1] rounded-[10px] font-['Inter'] text-base hover:bg-[#313131] transition-colors"
              >
                Connect Socials
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#1F1F1F] border-[#313131] p-6 rounded-xl w-[400px] max-w-[90vw]">
              <div className="flex justify-between items-center mb-8">
                <h2 className="text-white text-lg font-medium">Connect Your Socials</h2>
                <button
                  onClick={() => setIsDialogOpen(false)}
                  className="text-[#a1a1a1] hover:text-white transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="flex flex-col gap-4">
                {unconnectedPlatforms.map((platform) => (
                  <button
                    key={platform.name}
                    onClick={() => {
                      handleConnect(platform.name);
                      setIsDialogOpen(false);
                    }}
                    className={`flex items-center gap-3 px-4 py-2 rounded-lg text-[#a1a1a1] transition-colors ${platform.className}`}
                  >
                    <img
                      src={platform.icon}
                      alt={platform.name}
                      className="w-6 h-6"
                    />
                    <span>{platform.name}</span>
                  </button>
                ))}
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>
    </div>
  );
};