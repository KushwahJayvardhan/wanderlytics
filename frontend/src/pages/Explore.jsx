import { useEffect, useState } from "react";
import { fetchDestinations } from "../api/client";
import DestinationCard from "../components/DestinationCard";
import SearchBar from "../components/SearchBar";
import Skeleton from "../components/Skeleton";

const PAGE_SIZE = 9;

export default function Explore() {
  const [query, setQuery] = useState("");
  const [sortBy, setSortBy] = useState("popularity");
  const [page, setPage] = useState(0);
  const [data, setData] = useState({ results: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    const timeout = setTimeout(() => {
      fetchDestinations({ q: query, sortBy, limit: PAGE_SIZE, offset: page * PAGE_SIZE })
        .then((result) => {
          if (!cancelled) setData(result);
        })
        .catch(() => {
          if (!cancelled) setError("Couldn't load destinations. Is the API running?");
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    }, 300); // debounce search input

    return () => {
      cancelled = true;
      clearTimeout(timeout);
    };
  }, [query, sortBy, page]);

  const totalPages = Math.max(1, Math.ceil(data.total / PAGE_SIZE));

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <h1 className="text-2xl font-bold mb-4">Explore Destinations</h1>
      <SearchBar
        value={query}
        onChange={(v) => {
          setQuery(v);
          setPage(0);
        }}
        sortBy={sortBy}
        onSortChange={(v) => {
          setSortBy(v);
          setPage(0);
        }}
      />

      {error && (
        <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
      )}

      {loading ? (
        <Skeleton />
      ) : data.results.length === 0 ? (
        <p className="text-slate-500">No destinations found. Try a different search.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.results.map((destination) => (
            <DestinationCard key={destination.id} destination={destination} />
          ))}
        </div>
      )}

      {!loading && data.results.length > 0 && (
        <div className="flex items-center justify-center gap-4 mt-8">
          <button
            disabled={page === 0}
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            className="px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 disabled:opacity-40"
          >
            Previous
          </button>
          <span className="text-sm text-slate-500">
            Page {page + 1} of {totalPages}
          </span>
          <button
            disabled={page + 1 >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 disabled:opacity-40"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
