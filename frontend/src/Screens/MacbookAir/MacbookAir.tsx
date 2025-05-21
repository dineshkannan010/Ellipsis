import { MicIcon } from "lucide-react";
import React, { useState } from "react";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Card, CardContent } from "../../components/ui/card";

export const MacbookAir = (): JSX.Element => {
  const [postContent, setPostContent] = useState("");

  // Data for category badges
  const categories = [
    {
      icon: "/trending-up.svg",
      label: "Trending",
      alt: "Trending up",
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

  return (
    <div className="bg-[#1f1f1f] flex flex-row justify-center w-full min-h-screen">
      <div className="bg-[#1f1f1f] w-full max-w-[1280px] h-[832px] relative px-4 md:px-0">
        {/* Sidebar */}
        <div className="hidden md:block absolute w-[153px] h-[889px] top-[-29px] left-0 bg-[#121212]">
          {/* Logo and App Name */}
          <div className="flex w-[117px] items-center absolute top-8 left-[9px] gap-[11px]">
            <img
              className="w-12 h-12"
              alt="Steppers"
              src="/steppers-1.png"
            />
            <div className="font-['Inter'] text-[14px] text-[#f8f8f8]">
              Ellipsis
            </div>
          </div>

          {/* Sidebar Navigation Item */}
          <div className="flex w-[107px] items-center absolute top-[131px] left-[19px] gap-3">
            <img
              className="w-[22.12px] h-[22.12px]"
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
            <img
              className="w-8 h-8"
              alt="Steppers"
              src="/steppers-1.png"
            />
            <div className="font-['Inter'] text-[14px] text-[#f8f8f8]">
              Ellipsis
            </div>
          </div>
        </div>

        {/* Post Creation Card */}
        <div className="absolute w-full md:w-[722px] top-[461px] left-0 md:left-[289px] px-4 md:px-0">
          {/* Glow effect */}
          <div className="absolute w-full h-[176px] bg-[rgba(87,86,227,0.34)] rounded-[5px] blur-[119px]" />

          <Card className="absolute w-full md:w-[722px] h-auto md:h-[149px] top-[-7px] bg-[#1f1f1f] rounded-[15px] border border-solid border-[#313131]">
            <CardContent className="p-4 md:p-0 h-full relative">
              {/* Text input area */}
              <textarea
                value={postContent}
                onChange={(e) => setPostContent(e.target.value)}
                placeholder="Post About..."
                className="w-full md:w-[220px] h-[31px] md:absolute md:top-[25px] md:left-[29px] bg-transparent border-none outline-none resize-none font-['Inter'] text-base text-[#a1a1a1] focus:ring-0"
              />

              {/* MicIcon button */}
              <Button
                variant="ghost"
                className="hidden md:flex absolute w-[31px] h-[31px] top-[103px] left-[676px] p-[5px] bg-[#313131] rounded-[57px] items-center justify-center"
              >
                <MicIcon className="w-[14px] h-[19px] text-[#9388B3]" />
              </Button>

              {/* Category badges */}
              <div className="flex flex-wrap gap-2 md:gap-[25px] mt-4 md:mt-0 md:absolute md:top-[108px] md:left-[29px]">
                {categories.map((category, index) => (
                  <Badge
                    key={index}
                    className="flex h-[22.28px] items-center px-[6.96px] py-0 bg-[#313131] rounded-[6.96px]"
                  >
                    <img
                      className="w-[22.28px] h-[22.28px]"
                      alt={category.alt}
                      src={category.icon}
                    />
                    <span className="ml-1 font-['Inter'] text-[11.1px] text-[#a1a1a1] whitespace-nowrap">
                      {category.label}
                    </span>
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Welcome Section */}
        <div className="absolute w-full md:w-[402px] left-0 md:left-[449px] top-[182px] text-center px-4 md:px-0">
          {/* Loading Dots */}
          <div className="flex gap-2 justify-center mb-[36px]">
            <div className="w-2 h-2 rounded-full bg-[#9392e6]"></div>
            <div className="w-2 h-2 rounded-full bg-[#9392e6]"></div>
            <div className="w-2 h-2 rounded-full bg-[#9392e6]"></div>
          </div>
          
          <h1 className="font-['Inter'] font-medium text-xl md:text-2xl leading-[29px] text-white mb-[35px]">
            Welcome to <span className="text-[#9392e6]">Ellipsis</span>
          </h1>
        </div>

        {/* Description */}
        <p className="absolute w-full md:w-[556px] top-[324px] left-0 md:left-[344px] font-['Inter'] text-[13px] text-[#a1a1a1] text-center leading-[18px] px-4 md:px-0">
          Ellipsis is an AI content assistant that writes, refines, and
          schedules posts, optimising tone, strategy, and timing to grow your
          online presence with ease.
        </p>

        {/* Connect Socials Button */}
        <Button
          variant="outline"
          className="absolute h-8 px-5 py-0 top-[396px] left-1/2 transform -translate-x-1/2 md:left-[542px] md:transform-none bg-[#1F1F1F] border border-[#313131] text-[#a1a1a1] rounded-[10px] font-['Inter'] text-base hover:bg-[#313131] transition-colors"
        >
          Connect Socials
        </Button>
      </div>
    </div>
  );
};