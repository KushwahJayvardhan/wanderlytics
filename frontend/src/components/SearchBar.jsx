export default function SearchBar({ value, onChange, sortBy, onSortChange }) {
  return (
    <div className="flex flex-col sm:flex-row gap-3 mb-6">
      <input
        type="text"
        placeholder="Search destinations..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="flex-1 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500"
      />
      <select
        value={sortBy}
        onChange={(e) => onSortChange(e.target.value)}
        className="rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2"
      >
        <option value="popularity">Sort: Popularity</option>
        <option value="name">Sort: Name</option>
      </select>
    </div>
  );
}
