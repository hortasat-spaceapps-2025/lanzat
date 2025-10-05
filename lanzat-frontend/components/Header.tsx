export default function Header() {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
      <div className="container mx-auto px-3 sm:px-6 py-2 sm:py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 sm:space-x-4">
            <div className="text-xl sm:text-3xl">🌊</div>
            <div>
              <h1 className="text-base sm:text-2xl font-bold">Lanzat</h1>
              <p className="text-blue-100 text-[10px] sm:text-sm hidden sm:block">Hurricane Economic Vulnerability Platform for Florida</p>
              <p className="text-blue-100 text-[10px] sm:hidden">Florida Hurricane Platform</p>
            </div>
          </div>

          <div className="flex items-center">
            <div className="text-right">
              <p className="text-xs sm:text-sm text-blue-100">67 Counties</p>
              <p className="text-[10px] sm:text-xs text-blue-200 hidden sm:block">Real-time Assessment</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
