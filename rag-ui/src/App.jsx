import React from "react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import ChatBox from "./components/ChatBox/";

function App() {
  return (
    <div className="h-screen flex bg-gray-100">
      <Sidebar />
      <div className="flex-1 flex flex-col justify-between items-center p-4">
        <ChatBox /> {/* 👈 Add ChatBox directly */}
      </div>
    </div>
  );
}

export default App;
