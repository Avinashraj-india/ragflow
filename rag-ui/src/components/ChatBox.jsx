import React, { useState } from "react";
import { Send, Plus, LogOut, Upload, Bot, User, MessageSquare, Menu } from "lucide-react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import Paper from "@mui/material/Paper";
import IconButton from "@mui/material/IconButton";
import Avatar from "@mui/material/Avatar";
import Chip from "@mui/material/Chip";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Divider from "@mui/material/Divider";
import { styled } from "@mui/material/styles";

const backendURL = import.meta.env.VITE_BACKEND_URL;

const ChatContainer = styled(Box)(() => ({
  display: "flex",
  height: "100vh",
  width: "100vw",
  background: "#000",
  overflow: "hidden",
  margin: 0,
  padding: 0,
  position: "fixed",
  top: 0,
  left: 0,
}));

const Sidebar = styled(Box)(() => ({
  width: "260px",
  background: "#171717",
  display: "flex",
  flexDirection: "column",
  borderRadius: "0",
  margin: "0",
  border: "none",
}));

const MainContent = styled(Box)(() => ({
  flex: 1,
  display: "flex",
  flexDirection: "column",
  position: "relative",
  background: "#212121",
  borderRadius: "0",
  margin: "0",
  overflow: "hidden",
  border: "none",
}));

const SidebarHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderBottom: "1px solid #2d2d2d",
}));

const ChatHistoryItem = styled(ListItem)(({ theme, active }) => ({
  margin: theme.spacing(0.5, 1),
  borderRadius: "8px",
  cursor: "pointer",
  background: active ? "#2d2d2d" : "transparent",
  "&:hover": {
    background: "#2d2d2d",
  },
}));

const ChatHeader = styled(Box)(({ theme }) => ({
  background: "#212121",
  padding: theme.spacing(1.5, 3),
  borderBottom: "1px solid #2d2d2d",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  position: "sticky",
  top: 0,
  zIndex: 10,
}));

const MessagesContainer = styled(Box)(() => ({
  flex: 1,
  overflowY: "auto",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  padding: "20px 0",
  background: "#212121",
}));

const MessageWrapper = styled(Box)(({ sender }) => ({
  width: "100%",
  display: "flex",
  justifyContent: "center",
  padding: "12px 0",
  background: sender === "bot" ? "#2d2d2d" : "transparent",
}));

const MessageContent = styled(Box)(() => ({
  maxWidth: "768px",
  width: "100%",
  display: "flex",
  gap: "16px",
  padding: "0 20px",
}));

const InputContainer = styled(Box)(({ theme }) => ({
  background: "#212121",
  padding: theme.spacing(2),
  borderTop: "1px solid #2d2d2d",
  display: "flex",
  justifyContent: "center",
  position: "sticky",
  bottom: 0,
}));

const InputWrapper = styled(Box)(() => ({
  maxWidth: "768px",
  width: "100%",
  padding: "0 20px",
}));

const ChatBox = () => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [file, setFile] = useState(null);
  const [userTeam, setUserTeam] = useState("legal");
  const [chatHistory, setChatHistory] = useState([
    { id: 1, title: "Document Analysis", preview: "Can you analyze this contract?", active: false },
    { id: 2, title: "Legal Research", preview: "What are the implications of...", active: false },
    { id: 3, title: "Current Chat", preview: "How can I help you today?", active: true },
  ]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const navigate = useNavigate();

  React.useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        setUserTeam(payload.team || "legal");
      } catch (error) {
        console.error("Failed to decode token:", error);
      }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  const handleSend = async () => {
    if (!message.trim()) return;

    const userMessage = { text: message, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);

    // Update chat history with first message as title
    if (messages.length === 0) {
      setChatHistory(prev => prev.map(chat => 
        chat.active ? { ...chat, title: message.substring(0, 30) + (message.length > 30 ? '...' : ''), preview: message } : chat
      ));
    }

    try {
      const response = await axios.post(`${backendURL}/ask`, {
        query: message,
        group: userTeam.toLowerCase(),
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

  const handleNewChat = () => {
    setMessages([]);
    const newChatId = chatHistory.length + 1;
    setChatHistory(prev => [
      ...prev.map(chat => ({ ...chat, active: false })),
      { id: newChatId, title: "New Chat", preview: "How can I help you today?", active: true }
    ]);
  };

  const handleChatSelect = (chatId) => {
    setChatHistory(prev => prev.map(chat => ({ ...chat, active: chat.id === chatId })));
    // In a real app, you'd load the messages for this chat
    setMessages([]);
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
    <ChatContainer>
      {/* Sidebar */}
      <Sidebar>
        <SidebarHeader>
          <Button
            onClick={handleNewChat}
            variant="outlined"
            fullWidth
            startIcon={<Plus size={16} />}
            sx={{
              borderColor: "#4d4d4d",
              color: "#fff",
              "&:hover": { borderColor: "#6d6d6d", bgcolor: "#2d2d2d" }
            }}
          >
            New Chat
          </Button>
        </SidebarHeader>
        
        <Box sx={{ flex: 1, overflowY: "auto" }}>
          <List sx={{ p: 0 }}>
            {chatHistory.map((chat) => (
              <ChatHistoryItem
                key={chat.id}
                active={chat.active}
                onClick={() => handleChatSelect(chat.id)}
              >
                <MessageSquare size={16} style={{ marginRight: 12, color: "#9ca3af" }} />
                <ListItemText
                  primary={
                    <Typography
                      variant="body2"
                      sx={{ color: "#fff", fontWeight: chat.active ? 600 : 400 }}
                    >
                      {chat.title}
                    </Typography>
                  }
                  secondary={
                    <Typography variant="caption" sx={{ color: "#9ca3af" }}>
                      {chat.preview}
                    </Typography>
                  }
                />
              </ChatHistoryItem>
            ))}
          </List>
        </Box>
        
        <Box sx={{ p: 2, borderTop: "1px solid #2d2d2d" }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
            <Avatar sx={{ bgcolor: "#10a37f", width: 24, height: 24 }}>
              <User size={12} />
            </Avatar>
            <Typography variant="body2" sx={{ color: "#fff", flex: 1 }}>
              {userTeam} Team
            </Typography>
          </Box>
          <Button
            onClick={handleLogout}
            variant="text"
            fullWidth
            startIcon={<LogOut size={16} />}
            sx={{ color: "#9ca3af", justifyContent: "flex-start" }}
          >
            Logout
          </Button>
        </Box>
      </Sidebar>

      {/* Main Content */}
      <MainContent>
        {/* Header */}
        <ChatHeader>
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <IconButton
              onClick={() => setSidebarOpen(!sidebarOpen)}
              sx={{ color: "#9ca3af" }}
            >
              <Menu size={20} />
            </IconButton>
            <Avatar sx={{ bgcolor: "#10a37f", width: 32, height: 32 }}>
              <Bot size={18} />
            </Avatar>
            <Typography variant="h6" sx={{ fontWeight: 600, color: "#fff" }}>
              RAG Assistant
            </Typography>
            <Chip
              label={userTeam}
              size="small"
              sx={{ bgcolor: "#2d2d2d", color: "#fff" }}
            />
          </Box>
        </ChatHeader>

        {/* Messages */}
        <MessagesContainer>
        {messages.length === 0 && (
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              height: "60vh",
              maxWidth: "768px",
              textAlign: "center",
            }}
          >
            <Avatar sx={{ bgcolor: "#10a37f", width: 64, height: 64, mb: 3 }}>
              <Bot size={32} />
            </Avatar>
            <Typography variant="h4" sx={{ mb: 2, fontWeight: 600, color: "#fff" }}>
              How can I help you today?
            </Typography>
            <Typography variant="body1" sx={{ color: "#9ca3af", maxWidth: "400px" }}>
              I'm your RAG Assistant for the {userTeam} team. Ask me anything about your documents and knowledge base.
            </Typography>
          </Box>
        )}
        {messages.map((msg, index) => (
          <MessageWrapper key={index} sender={msg.sender}>
            <MessageContent>
              <Avatar
                sx={{
                  width: 32,
                  height: 32,
                  bgcolor: msg.sender === "user" ? "#19c37d" : "#10a37f",
                  flexShrink: 0,
                }}
              >
                {msg.sender === "user" ? <User size={16} /> : <Bot size={16} />}
              </Avatar>
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography 
                  variant="body1" 
                  sx={{ 
                    lineHeight: 1.6, 
                    color: "#fff",
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word"
                  }}
                >
                  {msg.text}
                </Typography>
              </Box>
            </MessageContent>
          </MessageWrapper>
        ))}
      </MessagesContainer>

        {/* Input Area */}
        <InputContainer>
        <InputWrapper>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <Box sx={{ display: "flex", gap: 1 }}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Message RAG Assistant..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
                multiline
                maxRows={4}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    borderRadius: "12px",
                    backgroundColor: "#2d2d2d",
                    border: "1px solid #4d4d4d",
                    color: "#fff",
                    "&:hover": {
                      borderColor: "#6d6d6d",
                    },
                    "&.Mui-focused": {
                      borderColor: "#10a37f",
                      boxShadow: "0 0 0 3px rgba(16, 163, 127, 0.1)",
                    },
                  },
                  "& .MuiInputBase-input::placeholder": {
                    color: "#9ca3af",
                  },
                }}
              />
              <IconButton
                onClick={handleSend}
                disabled={!message.trim()}
                sx={{
                  bgcolor: message.trim() ? "#10a37f" : "#f3f4f6",
                  color: message.trim() ? "white" : "#9ca3af",
                  "&:hover": { 
                    bgcolor: message.trim() ? "#0d8f6b" : "#e5e7eb" 
                  },
                  borderRadius: "8px",
                  width: 40,
                  height: 40,
                }}
              >
                <Send size={18} />
              </IconButton>
            </Box>
            
            <Box sx={{ display: "flex", alignItems: "center", gap: 1, justifyContent: "center" }}>
              <input
                type="file"
                onChange={(e) => setFile(e.target.files[0])}
                style={{ display: "none" }}
                id="file-upload"
              />
              <label htmlFor="file-upload">
                <Button
                  component="span"
                  variant="outlined"
                  size="small"
                  startIcon={<Upload size={14} />}
                  sx={{ 
                    borderColor: "#4d4d4d", 
                    color: "#9ca3af",
                    fontSize: "0.75rem",
                    "&:hover": { borderColor: "#6d6d6d" }
                  }}
                >
                  {file ? file.name.substring(0, 20) + (file.name.length > 20 ? '...' : '') : "Upload File"}
                </Button>
              </label>
              {file && (
                <Button
                  onClick={handleUpload}
                  variant="contained"
                  size="small"
                  startIcon={<Plus size={14} />}
                  sx={{ 
                    bgcolor: "#10a37f",
                    fontSize: "0.75rem",
                    "&:hover": { bgcolor: "#0d8f6b" }
                  }}
                >
                  Upload
                </Button>
              )}
            </Box>
          </Box>
        </InputWrapper>
        </InputContainer>
      </MainContent>
    </ChatContainer>
  );
};

export default ChatBox;
