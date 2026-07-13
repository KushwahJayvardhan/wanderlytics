import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { addFavorite, fetchDestination } from "../api/client";

export default function DestinationDetail() {
  const { id } = useParams();
  const [destination, setDestination] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    setLoading(true);
    fetchDestination(id)
      .then(setDestination)
      .finally(() => setLoading(false));
  }, [id]);

  async function handleFavorite() {
    try {
      await addFavorite(Number(id));
      setMessage("Added to favorites!");
    } catch {
      setMessage("Log in to save favorites.");
    }
    setTimeout(() => setMessage(""), 2500);
  }

  if (loading) return <p className="max-w-3xl mx-auto px-6 py-8">Loading...</p>;
  if (!destination) return <p className="max-w-3xl mx-auto px-6 py-8">Destination not found.</p>;

  return (
    <div className="max-w-3xl mx-auto px-6 py-8">
      <h1 className="text-3xl font-bold mb-2">{destination.name}</h1>
      <p className="text-slate-600 dark:text-slate-300 mb-6">{destination.description}</p>

      <div className="flex gap-3 mb-6">
        <button
          onClick={handleFavorite}
          className="px-4 py-2 rounded-lg bg-teal-600 text-white hover:bg-teal-700"
        >
          ♥ Save to favorites
        </button>
        {destination.source_url && (
          <a
            href={destination.source_url}
            target="_blank"
            rel="noreferrer"
            className="px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600"
          >
            View source
          </a>
        )}
      </div>

      {message && <p className="text-sm text-teal-600 dark:text-teal-400">{message}</p>}
    </div>
  );
}
