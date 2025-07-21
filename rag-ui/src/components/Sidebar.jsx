import React from "react";
import { Home, User, Folder, FileText } from "lucide-react";

const Sidebar = () => {
  return (
    <aside className="w-32 bg-[#0f172a] text-white flex flex-col items-center py-6 overflow-y-auto">
      {/* Logo */}
      <div className="text-purple-400 text-3xl font-bold mb-6">~</div>

      {/* New Chat Button */}
      <button className="w-24 bg-purple-600 hover:bg-purple-700 transition rounded p-2 text-sm mb-10">
        + New Chat
      </button>

      {/* Sidebar Icons */}
      <div className="flex flex-col gap-32 items-center mb-10">
        <Home className="cursor-pointer" stroke="white" />
        <User className="cursor-pointer" stroke="white" />
        <Folder className="cursor-pointer" stroke="white" />
        <FileText className="cursor-pointer" stroke="white" />
        
      </div>

      {/* Divider */}
      <div className="w-full border-t border-gray-700 mb-4"></div>

      {/* Recent Chats */}
      <div className="flex-1 w-full px-4 overflow-y-auto text-sm space-y-2">
        <div className="bg-slate-800 p-2 rounded cursor-pointer hover:bg-slate-700 transition">
          Project Update
        </div>
        <div className="bg-slate-800 p-2 rounded cursor-pointer hover:bg-slate-700 transition">
          RAGFlow Q&A
        </div>
        <div className="bg-slate-800 p-2 rounded cursor-pointer hover:bg-slate-700 transition">
          Private Notes
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
// refine the sidebar with a consistent color scheme and hover effects
// add hover effects to icons and recent chats
