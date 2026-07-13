import { useEffect, useState } from "react";
import { fetchFavorites } from "../api/client";
import DestinationCard from "../components/DestinationCard";
import Skeleton from "../components/Skeleton";

export default function Favorites() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFavorites()
      .then(setFavorites)
      .catch(() => setError("Log in to see your favorites."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <h1 className="text-2xl font-bold mb-4">Your Favorites</h1>
      {loading ? (
        <Skeleton count={3} />
      ) : error ? (
        <p className="text-slate-500">{error}</p>
      ) : favorites.length === 0 ? (
        <p className="text-slate-500">No favorites yet — go explore!</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {favorites.map((d) => (
            <DestinationCard key={d.id} destination={d} />
          ))}
        </div>
      )}
    </div>
  );
}
