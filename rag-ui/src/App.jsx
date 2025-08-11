// App.jsx
import React from "react";
import { Routes, Route } from "react-router-dom";
import SignInSide from "./components/sign-in-side/SignInSide.tsx"; // 👈 your login component
import Sidebar from "./components/Sidebar";
import ChatBox from "./components/ChatBox/";
import SignUp from "./components/sign-up/SignUp";
import AuthCallback from "./components/AuthCallback";

function App() {
  return (
    <Routes>
      <Route path="/" element={<SignInSide />} />
      <Route path="/signup" element={<SignUp />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
      <Route
        path="/chat"
        element={
          <div className="h-screen flex bg-black">
            <ChatBox /> {/* ✅ This will load exactly what you wrote */}
          </div>
        }
      />
    </Routes>
  );
}

export default App;
