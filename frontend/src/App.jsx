import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import axios from "axios";
import Dashboard from "./pages/Dashboard";
//import KanbanBoard from "./components/KanbanBoard";
//import Analytics from "./pages/Analytics";
import Login from "./pages/Login";
//import Navbar from "./components/Navbar";
//import ProtectedRoute from "./components/ProtectedRoute";

const App = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      axios
        .get("http://127.0.0.1:8000/api/user/", {
          headers: { Authorization: `Token ${token}` },
        })
        .then((res) => setUser(res.data))
        .catch(() => localStorage.removeItem("token"));
    }
  }, []);

  return (
    <Router>
      {user && <Navbar />}
      <Routes>
        <Route path="/" element={user ? <Navigate to="/dashboard" /> : <Login setUser={setUser} />} />
        <Route path="/dashboard" element={<ProtectedRoute user={user}><Dashboard /></ProtectedRoute>} />
        <Route path="/kanban" element={<ProtectedRoute user={user}><KanbanBoard /></ProtectedRoute>} />
        <Route path="/analytics" element={<ProtectedRoute user={user}><Analytics /></ProtectedRoute>} />
      </Routes>
    </Router>
  );
};

export default App;
