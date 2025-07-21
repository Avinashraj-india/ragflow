import React, { useState } from "react";
import { Paperclip } from "lucide-react";

export default function MessageBubble({ text, sender }) {
  const isUser = sender === "user";

  return (
    <div
      className={`flex items-end mb-3 ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div className="relative group max-w-[75%]">
        {/* Message bubble */}
        <div
          className={`px-4 py-2 rounded-lg text-sm shadow-md transition-all duration-300 ${
            isUser
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-black"
          }`}
        >
          {text}
        </div>

        {/* Upload icon (only for user, visible on hover) */}
        {isUser && (
          <label className="absolute -left-6 top-1/2 -translate-y-1/2 hidden group-hover:flex cursor-pointer items-center">
            <Paperclip size={16} className="text-gray-400 hover:text-white" />
            <input
              type="file"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files[0];
                if (file) {
                  console.log("Uploaded file:", file.name);
                }
              }}
            />
          </label>
        )}
      </div>
    </div>
  );
}
