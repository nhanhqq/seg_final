import React, { useState, useEffect } from 'react'
import { createBrowserRouter, RouterProvider, Link, useNavigate } from 'react-router-dom'
import { Moon, Sun, Search, Zap, Database, Code, Book, Star, Settings, Info, ExternalLink } from 'lucide-react'

// Theme Context
const ThemeContext = React.createContext()

// Theme Provider
function ThemeProvider({ children }) {
  const [darkMode, setDarkMode] = useState(() => {
    const savedTheme = localStorage.getItem('theme')
    return savedTheme ? savedTheme === 'dark' : true
  })

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }, [darkMode])

  return (
    <ThemeContext.Provider value={{ darkMode, setDarkMode }}>
      {children}
    </ThemeContext.Provider>
  )
}

// Liquid Glass Button Component
const GlassButton = ({ children, onClick, type = 'button', className = '' }) => {
  return (
    <button
      type={type}
      onClick={onClick}
      className={`px-6 py-3 rounded-full backdrop-blur-sm bg-white/10 dark:bg-black/10 border border-white/20 dark:border-white/10 hover:bg-white/20 dark:hover:bg-black/20 transition-all duration-300 group ${className}`}
    >
      <span className="flex items-center gap-2 text-white dark:text-white font-medium">
        {children}
      </span>
    </button>
  )
}

// Search Bar Component with Liquid Glass Effect
const SearchBar = ({ value, onChange, onSubmit }) => {
  const [query, setQuery] = useState(value || '')

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(query)
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Tìm kiếm tài liệu, giải pháp lập trình..."
          className="w-full py-4 pl-14 pr-20 rounded-full bg-white/80 dark:bg-black/20 backdrop-blur-md border border-white/20 dark:border-white/10 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent text-gray-800 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-all duration-300"
        />
        <GlassButton type="submit" className="absolute right-2 top-2 bottom-2">
          <Search className="h-4 w-4" />
          <span>Tìm kiếm</span>
        </GlassButton>
      </div>
    </form>
  )
}

// Theme Toggle Component
const ThemeToggle = () => {
  const { darkMode, setDarkMode } = React.useContext(ThemeContext)

  return (
    <button
      onClick={() => setDarkMode(!darkMode)}
      className="p-2 rounded-full bg-white/10 dark:bg-black/10 backdrop-blur-sm border border-white/20 dark:border-white/10 hover:bg-white/20 dark:hover:bg-black/20 transition-all duration-300"
      aria-label={darkMode ? 'Chuyển sang chế độ sáng' : 'Chuyển sang chế độ tối'}
    >
      {darkMode ? (
        <Sun className="h-5 w-5 text-yellow-400" />
      ) : (
        <Moon className="h-5 w-5 text-blue-400" />
      )}
    </button>
  )
}

// Quick Suggestion Pills
const SuggestionPill = ({ children, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="px-4 py-2 rounded-full bg-white/10 dark:bg-black/10 backdrop-blur-sm border border-white/10 dark:border-white/5 text-white/80 dark:text-white/80 hover:bg-white/20 dark:hover:bg-black/20 hover:text-white dark:hover:text-white transition-all duration-300 text-sm font-medium"
    >
      {children}
    </button>
  )
}

// Stats Card Component
const StatsCard = ({ icon, value, label }) => {
  const Icon = icon
  return (
    <div className="bg-white/5 dark:bg-black/10 backdrop-blur-sm rounded-xl p-4 border border-white/10 dark:border-white/5 flex items-center gap-3">
      <div className="p-3 rounded-lg bg-blue-500/20">
        <Icon className="h-6 w-6 text-blue-400" />
      </div>
      <div>
        <div className="text-2xl font-bold text-white">{value}</div>
        <div className="text-sm text-white/60">{label}</div>
      </div>
    </div>
  )
}

// Main Home Page
const HomePage = () => {
  const navigate = useNavigate()
  const { darkMode } = React.useContext(ThemeContext)

  const handleSearch = (query) => {
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query)}&algorithm=hybrid`)
    }
  }

  const quickSearches = [
    'Python Cơ bản',
    'React Hooks',
    'RESTful API',
    'Docker Compose',
    'Thuật toán QuickSort',
    'Machine Learning',
    'Blockchain',
    'Cloud Computing'
  ]

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background Effects */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-indigo-900/20"></div>
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIj48ZmlsdGVyIGlkPSJub2lzZSI+PGZlVHVyYnVsZW5jZSB0eXBlPSJmcmFjdGFsTm9pc2UiIGJhc2VGcmVxdWVuY3k9IjAuOCIgbnVtT2N0YXZlcz0iMyIvPjxmZUZ1bmN0aW9uIHR5cGU9InR1cmJ1bGVuY2UiIGZ1bmN0aW9uVHlwZT0iZ2VudW5vIiBzdGFydEZyZXF1ZW5jeT0iMCIgYmFzZUZyZXF1ZW5jeT0iMC4wNSIvPjwvZmlsdGVyPjxwYXRoIGQ9Ik0wIDBoMzAwdjMwMEgweiIgZmlsdGVyPSJ1cmwoI25vaXNlKSIgb3BhY2l0eT0iMC4xIi8+PC9zdmc+')]"></div>

        {/* Floating Glass Orbs */}
        <div className="absolute top-1/4 left-1/4 w-64 h-64 rounded-full bg-gradient-to-r from-blue-500/20 to-purple-500/20 blur-3xl animate-float"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full bg-gradient-to-r from-purple-500/20 to-indigo-500/20 blur-3xl animate-float-reverse"></div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8 min-h-screen flex flex-col">
        {/* Header */}
        <header className="flex justify-between items-center py-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
              <Code className="h-6 w-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white">Dev<span className="text-blue-400">Seek</span></h1>
          </div>

          <div className="flex items-center gap-3">
            <ThemeToggle />
            <GlassButton onClick={() => navigate('/about')}>
              <Info className="h-4 w-4" />
              <span>Giới thiệu</span>
            </GlassButton>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 flex flex-col items-center justify-center py-16">
          <div className="text-center mb-12">
            <h1 className="text-5xl md:text-6xl font-bold mb-4">
              <span className="text-white">Dev</span><span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Seek</span>
            </h1>
            <p className="text-xl text-white/80 max-w-2xl mx-auto">
              Máy tìm kiếm chuyên sâu cho tài liệu lập trình và công nghệ
            </p>
          </div>

          {/* Search Section */}
          <div className="w-full max-w-3xl mb-12">
            <SearchBar onSubmit={handleSearch} />

            {/* Quick Suggestions */}
            <div className="mt-8 flex flex-wrap justify-center gap-3">
              {quickSearches.map((suggestion, index) => (
                <SuggestionPill
                  key={index}
                  onClick={() => handleSearch(suggestion)}
                >
                  {suggestion}
                </SuggestionPill>
              ))}
            </div>
          </div>

          {/* Features Section */}
          <div className="grid md:grid-cols-3 gap-6 w-full max-w-5xl mt-16">
            <StatsCard icon={Database} value="1000+" label="Tài liệu" />
            <StatsCard icon={Zap} value="TF-IDF & BM25" label="Thuật toán" />
            <StatsCard icon={Star} value="4.9" label="Đánh giá" />
          </div>
        </main>

        {/* Footer */}
        <footer className="py-8 border-t border-white/10 mt-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-white/60 text-sm">
              © {new Date().getFullYear()} DevSeek. Máy tìm kiếm chuyên sâu cho lập trình viên.
            </p>
            <div className="flex gap-6 text-sm text-white/60">
              <a href="#" className="hover:text-white transition-colors">Điều khoản</a>
              <a href="#" className="hover:text-white transition-colors">Quyền riêng tư</a>
              <a href="#" className="hover:text-white transition-colors">Liên hệ</a>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}

// Search Results Page
const SearchResultsPage = () => {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('')
  const [stats, setStats] = useState({})
  const navigate = useNavigate()

  // Parse query params
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const searchQuery = params.get('q') || ''
    setQuery(searchQuery)

    if (searchQuery) {
      fetchResults(searchQuery)
    }
  }, [])

  const fetchResults = async (searchQuery) => {
    try {
      setLoading(true)
      const params = new URLSearchParams(window.location.search)
      const algorithm = params.get('algorithm') || 'hybrid'

      // Call backend API
      const response = await fetch(`/api/search?q=${encodeURIComponent(searchQuery)}&algorithm=${algorithm}`)
      const data = await response.json()

      setResults(data.results || [])
      setStats({
        total: data.total_results || 0,
        time: data.time_taken_ms || 0,
        algorithm: data.algorithm || 'TF-IDF'
      })
      setError(null)
    } catch (err) {
      setError('Không thể kết nối đến máy chủ tìm kiếm')
      console.error('Search error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (newQuery) => {
    if (newQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(newQuery)}`)
    }
  }

  return (
    <div className="min-h-screen relative">
      {/* Background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/10 via-purple-900/10 to-indigo-900/10"></div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="flex justify-between items-center py-6 mb-8">
          <Link to="/" className="flex items-center gap-3 text-white hover:text-blue-400 transition-colors">
            <Code className="h-6 w-6" />
            <span className="text-xl font-bold">Dev<span className="text-blue-400">Seek</span></span>
          </Link>

          <div className="flex items-center gap-3">
            <ThemeToggle />
            <GlassButton onClick={() => navigate('/')}>
              <Search className="h-4 w-4" />
              <span>Trang chủ</span>
            </GlassButton>
          </div>
        </header>

        {/* Search Bar */}
        <div className="mb-8">
          <SearchBar value={query} onSubmit={handleSearch} />
        </div>

        {/* Stats */}
        {stats.total > 0 && (
          <div className="mb-8 p-4 bg-white/5 dark:bg-black/10 backdrop-blur-sm rounded-xl border border-white/10 dark:border-white/5">
            <p className="text-white/80">
              Tìm thấy <span className="font-bold text-white">{stats.total}</span> kết quả cho
              <span className="font-bold text-blue-400 mx-1">"{query}"</span>
              trong <span className="font-bold text-white">{stats.time}ms</span> sử dụng
              <span className="font-bold text-purple-400 mx-1">{stats.algorithm}</span>
            </p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex-1 flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="flex-1 flex items-center justify-center py-20">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-red-500/20 rounded-full flex items-center justify-center">
                <Zap className="h-8 w-8 text-red-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Lỗi tìm kiếm</h3>
              <p className="text-white/80">{error}</p>
              <GlassButton onClick={() => fetchResults(query)} className="mt-4">
                <Search className="h-4 w-4" />
                <span>Thử lại</span>
              </GlassButton>
            </div>
          </div>
        )}

        {/* Results */}
        {!loading && !error && results.length > 0 && (
          <div className="space-y-6">
            {results.map((result, index) => (
              <ResultCard key={result.id || index} result={result} query={query} />
            ))}
          </div>
        )}

        {/* No Results */}
        {!loading && !error && results.length === 0 && (
          <div className="flex-1 flex items-center justify-center py-20">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-blue-500/20 rounded-full flex items-center justify-center">
                <Search className="h-8 w-8 text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Không tìm thấy kết quả</h3>
              <p className="text-white/80 mb-4">Thử với từ khóa khác hoặc kiểm tra chính tả</p>
              <div className="flex flex-wrap justify-center gap-3">
                {['Python', 'JavaScript', 'React', 'Algorithm'].map((suggestion) => (
                  <SuggestionPill key={suggestion} onClick={() => handleSearch(suggestion)}>
                    {suggestion}
                  </SuggestionPill>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Result Card Component
const ResultCard = ({ result, query }) => {
  const highlightText = (text, highlight) => {
    if (!highlight || !text) return text

    const parts = text.split(new RegExp(`(${highlight})`, 'gi'))
    return parts.map((part, i) =>
      part.toLowerCase() === highlight.toLowerCase() ? (
        <mark key={i} className="bg-yellow-300 text-gray-900 px-1 rounded">
          {part}
        </mark>
      ) : part
    )
  }

  return (
    <div className="bg-white/5 dark:bg-black/10 backdrop-blur-sm rounded-xl border border-white/10 dark:border-white/5 p-6 hover:border-blue-500/30 transition-all duration-300">
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-white mb-2">
            <a href={result.url} target="_blank" rel="noopener noreferrer" className="hover:text-blue-400 transition-colors">
              {highlightText(result.title, query)}
              <ExternalLink className="inline h-4 w-4 ml-1 text-blue-400" />
            </a>
          </h3>

          <p className="text-white/80 text-sm mb-3">
            {result.url && (
              <span className="break-all">
                {new URL(result.url).hostname}
              </span>
            )}
          </p>

          <p className="text-white/90 mb-4 leading-relaxed">
            {highlightText(result.snippet || result.summary || 'Không có mô tả', query)}
          </p>

          <div className="flex flex-wrap gap-2 mb-4">
            {result.tags && result.tags.map((tag, index) => (
              <span key={index} className="px-3 py-1 rounded-full bg-white/10 text-white/80 text-xs">
                {tag}
              </span>
            ))}
          </div>
        </div>

        <div className="flex flex-col items-end justify-between min-w-[120px]">
          <div className="text-right">
            <div className="text-2xl font-bold text-blue-400">{Math.round(result.score * 100)}</div>
            <div className="text-xs text-white/60">Điểm</div>
          </div>

          {result.category && (
            <span className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-400 text-xs mt-2">
              {result.category}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

// About Page
const AboutPage = () => {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen relative">
      {/* Background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/10 via-purple-900/10 to-indigo-900/10"></div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="flex justify-between items-center py-6 mb-8">
          <Link to="/" className="flex items-center gap-3 text-white hover:text-blue-400 transition-colors">
            <Code className="h-6 w-6" />
            <span className="text-xl font-bold">Dev<span className="text-blue-400">Seek</span></span>
          </Link>

          <div className="flex items-center gap-3">
            <ThemeToggle />
            <GlassButton onClick={() => navigate('/')}>
              <Search className="h-4 w-4" />
              <span>Trang chủ</span>
            </GlassButton>
          </div>
        </header>

        <main className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">
              <span className="text-white">Về</span> <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">DevSeek</span>
            </h1>
            <p className="text-xl text-white/80">
              Máy tìm kiếm chuyên sâu cho lập trình viên và nhà phát triển
            </p>
          </div>

          <div className="space-y-8">
            <FeatureCard
              icon={Search}
              title="Tìm kiếm thông minh"
              description="Sử dụng thuật toán TF-IDF và BM25 tiên tiến để tìm kiếm chính xác và nhanh chóng trong hàng nghìn tài liệu lập trình."
            />

            <FeatureCard
              icon={Zap}
              title="Hiệu suất tối ưu"
              description="Giao diện được tối ưu hóa với React và Vite, mang lại trải nghiệm mượt mà và nhanh chóng."
            />

            <FeatureCard
              icon={Moon}
              title="Chế độ tối/sáng"
              description="Hỗ trợ cả hai chế độ giao diện, bảo vệ mắt và tiết kiệm pin cho thiết bị của bạn."
            />

            <FeatureCard
              icon={Code}
              title="Dành cho lập trình viên"
              description="Được thiết kế đặc biệt cho cộng đồng lập trình viên với các tính năng tìm kiếm chuyên sâu."
            />
          </div>

          <div className="mt-16 text-center">
            <GlassButton onClick={() => navigate('/')}>
              <Search className="h-4 w-4" />
              <span>Bắt đầu tìm kiếm</span>
            </GlassButton>
          </div>
        </main>
      </div>
    </div>
  )
}

// Feature Card Component
const FeatureCard = ({ icon: Icon, title, description }) => {
  return (
    <div className="bg-white/5 dark:bg-black/10 backdrop-blur-sm rounded-xl border border-white/10 dark:border-white/5 p-6 hover:border-blue-500/30 transition-all duration-300">
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 p-3 rounded-lg bg-blue-500/20">
          <Icon className="h-6 w-6 text-blue-400" />
        </div>
        <div>
          <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
          <p className="text-white/80 leading-relaxed">{description}</p>
        </div>
      </div>
    </div>
  )
}

// Router Setup
const router = createBrowserRouter([
  {
    path: '/',
    element: <HomePage />
  },
  {
    path: '/search',
    element: <SearchResultsPage />
  },
  {
    path: '/about',
    element: <AboutPage />
  }
])

// Main App Component
function App() {
  return (
    <ThemeProvider>
      <RouterProvider router={router} />
    </ThemeProvider>
  )
}

export default App