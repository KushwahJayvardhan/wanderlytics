import { Link } from "react-router-dom";

export default function Navbar({ darkMode, onToggleDarkMode, isLoggedIn, onLogout }) {
  return (
    <nav className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-700">
      <Link to="/" className="text-xl font-bold text-teal-600 dark:text-teal-400">
        TripScope
      </Link>
      <div className="flex items-center gap-4 text-sm">
        <Link to="/" className="hover:text-teal-600">
          Explore
        </Link>
        <Link to="/favorites" className="hover:text-teal-600">
          Favorites
        </Link>
        {isLoggedIn ? (
          <button onClick={onLogout} className="hover:text-teal-600">
            Log out
          </button>
        ) : (
          <Link to="/login" className="hover:text-teal-600">
            Log in
          </Link>
        )}
        <button
          onClick={onToggleDarkMode}
          className="rounded-full px-3 py-1 border border-slate-300 dark:border-slate-600"
          aria-label="Toggle dark mode"
        >
          {darkMode ? "☀️" : "🌙"}
        </button>
      </div>
    </nav>
  );
}
