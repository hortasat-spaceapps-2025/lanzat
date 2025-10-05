export default function Legend() {
  const categories = [
    { label: 'Critical', color: '#8B0000', range: '80-100%' },
    { label: 'High', color: '#DC143C', range: '60-80%' },
    { label: 'Moderate', color: '#FF8C00', range: '40-60%' },
    { label: 'Low', color: '#FFD700', range: '20-40%' },
    { label: 'Very Low', color: '#FFFFE0', range: '0-20%' }
  ];

  return (
    <div className="absolute bottom-3 sm:bottom-6 left-3 sm:left-6 bg-white rounded-lg shadow-lg p-2 sm:p-4 z-[1000] max-w-[200px] sm:max-w-none">
      <h3 className="font-bold text-xs sm:text-sm mb-2 sm:mb-3 text-gray-800">Vulnerability</h3>
      <div className="space-y-1 sm:space-y-2">
        {categories.map((cat) => (
          <div key={cat.label} className="flex items-center space-x-2 sm:space-x-3">
            <div
              className="w-4 h-4 sm:w-6 sm:h-6 rounded border border-gray-300 flex-shrink-0"
              style={{ backgroundColor: cat.color }}
            />
            <div className="text-xs sm:text-sm">
              <span className="font-semibold">{cat.label}</span>
              <span className="text-gray-500 ml-1 sm:ml-2 text-[10px] sm:text-xs">{cat.range}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
