import { useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import DestinationDetail from "./pages/DestinationDetail";
import Explore from "./pages/Explore";
import Favorites from "./pages/Favorites";
import Login from "./pages/Login";

export default function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem("tripscope_token"));

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  function handleLogout() {
    localStorage.removeItem("tripscope_token");
    setIsLoggedIn(false);
  }

  return (
    <div className="min-h-screen">
      <Navbar
        darkMode={darkMode}
        onToggleDarkMode={() => setDarkMode((d) => !d)}
        isLoggedIn={isLoggedIn}
        onLogout={handleLogout}
      />
      <Routes>
        <Route path="/" element={<Explore />} />
        <Route path="/destinations/:id" element={<DestinationDetail />} />
        <Route path="/favorites" element={<Favorites />} />
        <Route path="/login" element={<Login onLoggedIn={() => setIsLoggedIn(true)} />} />
      </Routes>
    </div>
  );
}
