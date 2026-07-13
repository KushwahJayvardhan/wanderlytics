export default function Skeleton({ count = 6 }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="animate-pulse rounded-xl border border-slate-200 dark:border-slate-700 p-4 h-28 bg-slate-100 dark:bg-slate-800"
        />
      ))}
    </div>
  );
}
