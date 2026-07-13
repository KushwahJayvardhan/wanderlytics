import { Link } from "react-router-dom";

export default function DestinationCard({ destination }) {
  return (
    <Link
      to={`/destinations/${destination.id}`}
      className="block rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-lg transition-shadow bg-white dark:bg-slate-800"
    >
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-semibold">{destination.name}</h3>
        <span className="text-xs px-2 py-1 rounded-full bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200">
          {Math.round(destination.popularity_score)} pts
        </span>
      </div>
      <p className="text-sm text-slate-600 dark:text-slate-300 line-clamp-3">
        {destination.short_description || destination.description}
      </p>
    </Link>
  );
}
