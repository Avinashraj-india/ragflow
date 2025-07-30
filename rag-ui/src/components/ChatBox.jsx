import React, { useState } from "react";
import { Send, Plus } from "lucide-react";
import axios from "axios";

const backendURL = import.meta.env.VITE_BACKEND_URL;

const ChatBox = () => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [file, setFile] = useState(null); // ⬅️ New state

  const handleSend = async () => {
    if (!message.trim()) return;

    const userMessage = { text: message, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await axios.post(`${backendURL}/ask`, {
        query: message,
        group: "legal",
        llm: "ollama",
      });

      const botReply = {
        text: response?.data?.response || "No response",
        sender: "bot",
      };

      setMessages((prev) => [...prev, botReply]);
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        { text: "Failed to reach server.", sender: "bot" },
      ]);
    }

    setMessage("");
  };

  // ⬇️ Upload handler
  const handleUpload = async () => {
    if (!file) return alert("Please select a file first.");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(`${backendURL}/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      alert("File uploaded and indexed.");
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Upload failed.");
    }
  };

  return (
    <div className="flex flex-col h-full w-full bg-gray-50 p-6 rounded-xl">
      {/* Chat history */}
      <div className="flex-1 overflow-y-auto mb-4 p-4 bg-white border rounded-md shadow-sm space-y-3">
        {messages.length === 0 && (
          <p className="text-gray-400 italic text-center">
            Start a conversation with the RAG Bot 👇
          </p>
        )}
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`max-w-md px-4 py-2 rounded-lg ${
              msg.sender === "user"
                ? "bg-blue-600 text-white self-end ml-auto rounded-br-none"
                : "bg-gray-200 text-black self-start mr-auto rounded-bl-none"
            }`}
          >
            {msg.text}
          </div>
        ))}
      </div>

      {/* Input + Send */}
      <div className="flex items-center border rounded-md shadow-sm bg-white px-4 py-2 mb-2">
        <input
          type="text"
          placeholder="Ask a question..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          className="flex-1 outline-none bg-transparent text-gray-800 placeholder:text-gray-400"
        />
        <button
          onClick={handleSend}
          className="text-blue-600 hover:text-blue-800 transition"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>

      {/* File input + Upload */}
      <div className="flex items-center space-x-2">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          className="text-sm"
        />
        <button
          onClick={handleUpload}
          className="flex items-center px-3 py-1.5 bg-green-600 text-white rounded hover:bg-green-700"
        >
          <Plus className="w-4 h-4 mr-1" />
          Upload
        </button>
      </div>
    </div>
  );
};

export default ChatBox;
