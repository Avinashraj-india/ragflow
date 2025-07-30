// App.jsx
import React from "react";
import { Routes, Route } from "react-router-dom";
import SignInSide from './components/sign-in-side/SignInSide.tsx';     // 👈 your login component
import Sidebar from "./components/Sidebar";
import ChatBox from "./components/ChatBox/";

function App() {
  return (
    <Routes>
      <Route path="/" element={<SignInSide />} />
      <Route
        path="/chat"
        element={
          <div className="h-screen flex bg-gray-100">
            <Sidebar />
            <div className="flex-1 flex flex-col justify-between items-center p-4">
              <ChatBox />  {/* ✅ This will load exactly what you wrote */}
            </div>
          </div>
        }
      />
    </Routes>
  );
}

export default App;
