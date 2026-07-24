import { createBrowserRouter, RouterProvider, Link, useNavigate, useLocation } from 'react-router-dom'
import {
  Moon, Sun, Search, Zap, Database, Code, Book, Star, Settings, Info, ExternalLink,
  Sparkles, TrendingUp, Clock, Filter, Download, Share2, Heart, Eye, ChevronRight,
  Command, X, ArrowRight, BarChart3, Users, Globe, Hash, Tag, Award, Activity,
  Bookmark, History, Coffee, Zap as Lightning, Mic, Camera, Wand2, Layers,
  Grid, List, ChevronDown, Star as StarIcon, MoreVertical, Calendar, User
} from 'lucide-react'
import { motion, AnimatePresence, useScroll, useTransform, useSpring, useMotionValue } from 'framer-motion'

// ============================================================
// THEME SYSTEM
// ============================================================
const ThemeContext = React.createContext()

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

// ============================================================
// PARTICLE BACKGROUND - Animated floating particles
// ============================================================
const ParticleBackground = ({ count = 50 }) => {
  const particles = useMemo(() =>
    Array.from({ length: count }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 4 + 1,
      duration: Math.random() * 20 + 10,
      delay: Math.random() * 5
    })), [count])

  return (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
      {particles.map(p => (
        <motion.div
          key={p.id}
          className="absolute rounded-full bg-gradient-to-r from-blue-400/30 to-purple-400/30 blur-sm"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: p.size,
            height: p.size,
          }}
          animate={{
            y: [0, -30, 0],
            x: [0, 20, -20, 0],
            scale: [1, 1.5, 1],
            opacity: [0.3, 0.8, 0.3]
          }}
          transition={{
            duration: p.duration,
            delay: p.delay,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      ))}
    </div>
  )
}

// ============================================================
// ANIMATED GRID BACKGROUND
// ============================================================
const GridBackground = () => (
  <div className="fixed inset-0 -z-20 overflow-hidden">
    <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900 dark:from-slate-950 dark:via-purple-950/30 dark:to-slate-950" />
    <div
      className="absolute inset-0 opacity-30"
      style={{
        backgroundImage: `
          linear-gradient(rgba(99, 102, 241, 0.1) 1px, transparent 1px),
          linear-gradient(90deg, rgba(99, 102, 241, 0.1) 1px, transparent 1px)
        `,
        backgroundSize: '50px 50px',
        maskImage: 'radial-gradient(ellipse at center, black 0%, transparent 70%)',
        WebkitMaskImage: 'radial-gradient(ellipse at center, black 0%, transparent 70%)'
      }}
    />
  </div>
)

// ============================================================
// GLASS CARD - Liquid Glass with advanced effects
// ============================================================
const GlassCard = ({ children, className = '', hoverable = true, glow = false, ...props }) => (
  <motion.div
    whileHover={hoverable ? {
      y: -4,
      scale: 1.02,
      transition: { duration: 0.2 }
    } : {}}
    className={`relative backdrop-blur-xl bg-white/5 dark:bg-white/5 border border-white/10 rounded-2xl overflow-hidden ${glow ? 'shadow-2xl shadow-blue-500/20' : ''} ${className}`}
    {...props}
  >
    {glow && (
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 opacity-0 hover:opacity-100 transition-opacity duration-500" />
    )}
    <div className="relative z-10">{children}</div>
  </motion.div>
)

// ============================================================
// GLASS BUTTON - With ripple effect
// ============================================================
const GlassButton = ({ children, onClick, type = 'button', className = '', variant = 'default', ...props }) => {
  const variants = {
    default: 'bg-white/10 hover:bg-white/20 border-white/20',
    primary: 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 border-transparent shadow-lg shadow-blue-500/30',
    ghost: 'bg-transparent hover:bg-white/10 border-transparent',
  }

  return (
    <motion.button
      type={type}
      onClick={onClick}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className={`relative px-6 py-3 rounded-full backdrop-blur-sm border transition-all duration-300 group overflow-hidden ${variants[variant]} ${className}`}
      {...props}
    >
      <span className="relative z-10 flex items-center gap-2 text-white font-medium">
        {children}
      </span>
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
        initial={{ x: '-100%' }}
        whileHover={{ x: '100%' }}
        transition={{ duration: 0.6 }}
      />
    </motion.button>
  )
}

// ============================================================
// THEME TOGGLE - Animated sun/moon
// ============================================================
const ThemeToggle = () => {
  const { darkMode, setDarkMode } = React.useContext(ThemeContext)

  return (
    <motion.button
      onClick={() => setDarkMode(!darkMode)}
      whileHover={{ scale: 1.1, rotate: 15 }}
      whileTap={{ scale: 0.9 }}
      className="relative p-3 rounded-full bg-white/10 dark:bg-black/20 backdrop-blur-xl border border-white/20 hover:bg-white/20 transition-all duration-300 group"
      aria-label={darkMode ? 'Chuyển sang chế độ sáng' : 'Chuyển sang chế độ tối'}
    >
      <AnimatePresence mode="wait">
        {darkMode ? (
          <motion.div
            key="sun"
            initial={{ rotate: -180, opacity: 0, scale: 0 }}
            animate={{ rotate: 0, opacity: 1, scale: 1 }}
            exit={{ rotate: 180, opacity: 0, scale: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Sun className="h-5 w-5 text-yellow-400" />
          </motion.div>
        ) : (
          <motion.div
            key="moon"
            initial={{ rotate: 180, opacity: 0, scale: 0 }}
            animate={{ rotate: 0, opacity: 1, scale: 1 }}
            exit={{ rotate: -180, opacity: 0, scale: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Moon className="h-5 w-5 text-blue-400" />
          </motion.div>
        )}
      </AnimatePresence>
      <div className="absolute inset-0 rounded-full bg-gradient-to-r from-yellow-400/0 to-blue-400/0 group-hover:from-yellow-400/20 group-hover:to-blue-400/20 transition-all duration-300" />
    </motion.button>
  )
}

// ============================================================
// SEARCH HISTORY HOOK
// ============================================================
const useSearchHistory = () => {
  const [history, setHistory] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('searchHistory') || '[]')
    } catch { return [] }
  })

  const addToHistory = useCallback((query) => {
    if (!query.trim()) return
    setHistory(prev => {
      const filtered = prev.filter(item => item.query !== query)
      const newHistory = [{ query, timestamp: Date.now() }, ...filtered].slice(0, 10)
      localStorage.setItem('searchHistory', JSON.stringify(newHistory))
      return newHistory
    })
  }, [])

  const clearHistory = useCallback(() => {
    setHistory([])
    localStorage.removeItem('searchHistory')
  }, [])

  return { history, addToHistory, clearHistory }
}

// ============================================================
// STATS CARD - Animated
// ============================================================
const StatsCard = ({ icon: Icon, value, label, color = 'blue', delay = 0 }) => {
  const colors = {
    blue: 'from-blue-500 to-cyan-500',
    purple: 'from-purple-500 to-pink-500',
    green: 'from-green-500 to-emerald-500',
    orange: 'from-orange-500 to-red-500',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      whileHover={{ y: -8, scale: 1.03 }}
      className="relative group"
    >
      <GlassCard className="p-6" glow>
        <div className="flex items-center gap-4">
          <motion.div
            whileHover={{ rotate: 360 }}
            transition={{ duration: 0.6 }}
            className={`p-3 rounded-xl bg-gradient-to-br ${colors[color]} shadow-lg`}
          >
            <Icon className="h-6 w-6 text-white" />
          </motion.div>
          <div>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: delay + 0.2 }}
              className="text-2xl font-bold text-white"
            >
              {value}
            </motion.div>
            <div className="text-sm text-white/60">{label}</div>
          </div>
        </div>
      </GlassCard>
    </motion.div>
  )
}

// ============================================================
// ANIMATED SEARCH BAR - With voice/AI suggestions
// ============================================================
const AnimatedSearchBar = ({ onSearch, initialQuery = '', placeholder = "Tìm kiếm tài liệu, giải pháp lập trình..." }) => {
  const [query, setQuery] = useState(initialQuery)
  const [isFocused, setIsFocused] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const inputRef = useRef(null)

  // Keyboard shortcut: Cmd+K or Ctrl+K
  useEffect(() => {
    const handler = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        inputRef.current?.focus()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) onSearch(query.trim())
  }

  return (
    <motion.form
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-3xl mx-auto"
    >
      <motion.div
        animate={{
          scale: isFocused ? 1.02 : 1,
        }}
        transition={{ duration: 0.2 }}
        className="relative"
      >
        {/* Glow effect when focused */}
        <AnimatePresence>
          {isFocused && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute -inset-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full blur-lg opacity-50"
            />
          )}
        </AnimatePresence>

        <div className="relative flex items-center bg-white/10 dark:bg-black/20 backdrop-blur-xl rounded-full border border-white/20 overflow-hidden">
          <div className="pl-6 pr-2">
            <Search className="h-5 w-5 text-white/60" />
          </div>

          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={placeholder}
            className="flex-1 py-4 px-2 bg-transparent text-white placeholder-white/50 outline-none text-lg"
          />

          <div className="flex items-center gap-2 pr-2">
            <kbd className="hidden sm:inline-flex items-center gap-1 px-2 py-1 text-xs text-white/50 bg-white/5 rounded border border-white/10">
              <Command className="h-3 w-3" />K
            </kbd>
            <motion.button
              type="submit"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-medium rounded-full transition-all duration-300 shadow-lg shadow-blue-500/30 flex items-center gap-2"
            >
              <span className="hidden sm:inline">Tìm</span>
              <ArrowRight className="h-4 w-4" />
            </motion.button>
          </div>
        </div>
      </motion.div>
    </motion.form>
  )
}

// ============================================================
// HOME PAGE
// ============================================================
const HomePage = () => {
  const navigate = useNavigate()
  const { history, addToHistory, clearHistory } = useSearchHistory()

  const handleSearch = (query) => {
    addToHistory(query)
    navigate(`/search?q=${encodeURIComponent(query)}&algorithm=hybrid`)
  }

  const quickSearches = [
    { label: 'Python Cơ bản', icon: '🐍', color: 'from-blue-500 to-cyan-500' },
    { label: 'React Hooks', icon: '⚛️', color: 'from-cyan-500 to-blue-500' },
    { label: 'RESTful API', icon: '🔌', color: 'from-purple-500 to-pink-500' },
    { label: 'Docker Compose', icon: '🐳', color: 'from-blue-500 to-indigo-500' },
    { label: 'QuickSort', icon: '⚡', color: 'from-yellow-500 to-orange-500' },
    { label: 'Machine Learning', icon: '🤖', color: 'from-green-500 to-emerald-500' },
    { label: 'Blockchain', icon: '⛓️', color: 'from-purple-500 to-indigo-500' },
    { label: 'Cloud Computing', icon: '☁️', color: 'from-sky-500 to-blue-500' },
  ]

  return (
    <div className="min-h-screen relative">
      <GridBackground />
      <ParticleBackground count={30} />

      <div className="relative z-10 container mx-auto px-4 py-8 min-h-screen flex flex-col">
        {/* Animated Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex justify-between items-center py-6"
        >
          <Link to="/" className="flex items-center gap-3 group">
            <motion.div
              whileHover={{ rotate: 360, scale: 1.1 }}
              transition={{ duration: 0.6 }}
              className="w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30"
            >
              <Code className="h-7 w-7 text-white" />
            </motion.div>
            <div>
              <h1 className="text-2xl font-bold text-white">Dev<span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Seek</span></h1>
              <p className="text-xs text-white/50">Powered by AI</p>
            </div>
          </Link>

          <div className="flex items-center gap-3">
            <ThemeToggle />
            <GlassButton onClick={() => navigate('/about')} variant="ghost">
              <Info className="h-4 w-4" />
              <span className="hidden sm:inline">Giới thiệu</span>
            </GlassButton>
          </div>
        </motion.header>

        {/* Hero Section */}
        <main className="flex-1 flex flex-col items-center justify-center py-12">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, type: "spring" }}
            className="text-center mb-12"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm mb-6"
            >
              <Sparkles className="h-4 w-4 text-yellow-400" />
              <span className="text-sm text-white/80">AI-Powered Search Engine</span>
            </motion.div>

            <h1 className="text-6xl md:text-8xl font-black mb-6">
              <motion.span
                className="inline-block text-white"
                initial={{ x: -50, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.3, duration: 0.5 }}
              >
                Dev
              </motion.span>
              <motion.span
                className="inline-block bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent"
                initial={{ x: 50, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.4, duration: 0.5 }}
              >
                Seek
              </motion.span>
            </h1>

            <motion.p
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.5, duration: 0.5 }}
              className="text-xl text-white/70 max-w-2xl mx-auto"
            >
              Tìm kiếm tài liệu lập trình với công nghệ <span className="text-blue-400 font-semibold">TF-IDF</span> và <span className="text-purple-400 font-semibold">BM25</span> tiên tiến
            </motion.p>
          </motion.div>

          {/* Search Bar */}
          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.5 }}
            className="w-full max-w-3xl mb-10"
          >
            <AnimatedSearchBar onSearch={handleSearch} />
          </motion.div>

          {/* Quick Suggestions */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.7, duration: 0.5 }}
            className="w-full max-w-3xl mb-12"
          >
            <div className="flex items-center gap-2 mb-4 text-sm text-white/60">
              <Sparkles className="h-4 w-4" />
              <span>Gợi ý phổ biến</span>
            </div>
            <div className="flex flex-wrap gap-3">
              {quickSearches.map((item, index) => (
                <motion.button
                  key={item.label}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.8 + index * 0.05 }}
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => handleSearch(item.label)}
                  className={`group relative px-4 py-2 rounded-full bg-gradient-to-r ${item.color} bg-opacity-10 border border-white/10 hover:border-white/30 text-white text-sm font-medium transition-all duration-300 overflow-hidden`}
                >
                  <span className="relative z-10 flex items-center gap-2">
                    <span className="text-lg">{item.icon}</span>
                    {item.label}
                  </span>
                  <motion.div
                    className="absolute inset-0 bg-white/10"
                    initial={{ x: '-100%' }}
                    whileHover={{ x: '100%' }}
                    transition={{ duration: 0.6 }}
                  />
                </motion.button>
              ))}
            </div>
          </motion.div>

          {/* Search History */}
          {history.length > 0 && (
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.9, duration: 0.5 }}
              className="w-full max-w-3xl mb-12"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2 text-sm text-white/60">
                  <History className="h-4 w-4" />
                  <span>Tìm kiếm gần đây</span>
                </div>
                <button
                  onClick={clearHistory}
                  className="text-xs text-white/40 hover:text-white/80 transition-colors"
                >
                  Xóa tất cả
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {history.slice(0, 5).map((item, index) => (
                  <motion.button
                    key={item.query}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    whileHover={{ scale: 1.05 }}
                    onClick={() => handleSearch(item.query)}
                    className="px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-white/70 hover:text-white text-sm transition-all"
                  >
                    {item.query}
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}

          {/* Stats Section */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 1, duration: 0.5 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full max-w-5xl"
          >
            <StatsCard icon={Database} value="1000+" label="Tài liệu" color="blue" delay={1.0} />
            <StatsCard icon={Zap} value="<10ms" label="Tốc độ" color="purple" delay={1.1} />
            <StatsCard icon={Users} value="10K+" label="Người dùng" color="green" delay={1.2} />
            <StatsCard icon={Award} value="4.9★" label="Đánh giá" color="orange" delay={1.3} />
          </motion.div>
        </main>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5, duration: 0.5 }}
          className="py-8 border-t border-white/10 mt-auto"
        >
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-white/40 text-sm">
              © 2024 DevSeek • Made with <Heart className="inline h-3 w-3 text-red-400" /> in Vietnam
            </p>
            <div className="flex gap-6 text-sm text-white/40">
              <a href="#" className="hover:text-white transition-colors">Điều khoản</a>
              <a href="#" className="hover:text-white transition-colors">Quyền riêng tư</a>
              <a href="#" className="hover:text-white transition-colors">API</a>
            </div>
          </div>
        </motion.footer>
      </div>
    </div>
  )
}

// ============================================================
// RESULT CARD - With HTML rendering for highlight
// ============================================================
const ResultCard = ({ result, query, index, viewMode = 'list' }) => {
  // Parse the HTML to extract highlighted parts
  const renderHTML = (htmlString) => {
    if (!htmlString) return null
    return { __html: htmlString }
  }

  const formattedDate = useMemo(() => {
    if (!result.date) return null
    try {
      return new Date(result.date).toLocaleDateString('vi-VN')
    } catch { return result.date }
  }, [result.date])

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
    >
      <GlassCard className="p-6 group cursor-pointer">
        <div className="flex flex-col md:flex-row gap-6">
          {/* Main Content */}
          <div className="flex-1 min-w-0">
            {/* Title with HTML rendering */}
            <h3 className="text-xl font-semibold mb-2">
              <a
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-white hover:text-blue-400 transition-colors flex items-center gap-2 group"
                dangerouslySetInnerHTML={renderHTML(result.title)}
              />
            </h3>

            {/* URL */}
            {result.url && (
              <div className="flex items-center gap-2 text-sm text-green-400/70 mb-3">
                <Globe className="h-3 w-3" />
                <span className="truncate">
                  {(() => {
                    try { return new URL(result.url).hostname }
                    catch { return result.url }
                  })()}
                </span>
              </div>
            )}

            {/* Snippet with HTML rendering */}
            <p
              className="text-white/80 leading-relaxed mb-4 line-clamp-3"
              dangerouslySetInnerHTML={renderHTML(result.snippet || result.summary)}
            />

            {/* Tags */}
            {result.tags && result.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-3">
                {result.tags.slice(0, 4).map((tag, i) => (
                  <motion.span
                    key={i}
                    whileHover={{ scale: 1.05 }}
                    className="px-3 py-1 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-white/70 text-xs transition-colors"
                  >
                    <Hash className="inline h-3 w-3 mr-1" />
                    {tag}
                  </motion.span>
                ))}
              </div>
            )}

            {/* Meta info */}
            <div className="flex flex-wrap items-center gap-4 text-xs text-white/50">
              {result.author && (
                <span className="flex items-center gap-1">
                  <User className="h-3 w-3" />
                  {result.author}
                </span>
              )}
              {formattedDate && (
                <span className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  {formattedDate}
                </span>
              )}
              {result.category && (
                <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-blue-500/10 text-blue-400">
                  <Tag className="h-3 w-3" />
                  {result.category}
                </span>
              )}
            </div>
          </div>

          {/* Score & Actions */}
          <div className="flex md:flex-col items-end justify-between md:justify-start gap-3 md:min-w-[120px]">
            {/* Score circle */}
            <motion.div
              whileHover={{ scale: 1.1, rotate: 5 }}
              className="relative w-16 h-16 flex items-center justify-center"
            >
              <svg className="absolute inset-0" viewBox="0 0 36 36">
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="rgba(255,255,255,0.1)"
                  strokeWidth="3"
                />
                <motion.path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="url(#gradient)"
                  strokeWidth="3"
                  strokeLinecap="round"
                  initial={{ strokeDasharray: "0, 100" }}
                  animate={{ strokeDasharray: `${(result.score || 0) * 100}, 100` }}
                  transition={{ duration: 1, delay: index * 0.1 }}
                />
                <defs>
                  <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#3b82f6" />
                    <stop offset="100%" stopColor="#a855f7" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="relative text-center">
                <div className="text-lg font-bold text-white">
                  {Math.round((result.score || 0) * 100)}
                </div>
                <div className="text-[10px] text-white/50">SCORE</div>
              </div>
            </motion.div>

            {/* Action buttons */}
            <div className="flex md:flex-col gap-2">
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="p-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-white/60 hover:text-white transition-colors"
                title="Lưu"
              >
                <Bookmark className="h-4 w-4" />
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="p-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-white/60 hover:text-white transition-colors"
                title="Chia sẻ"
              >
                <Share2 className="h-4 w-4" />
              </motion.button>
            </div>
          </div>
        </div>
      </GlassCard>
    </motion.div>
  )
}

// ============================================================
// SEARCH RESULTS PAGE
// ============================================================
const SearchResultsPage = () => {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('')
  const [stats, setStats] = useState({})
  const [viewMode, setViewMode] = useState('list')
  const [sortBy, setSortBy] = useState('relevance')
  const [algorithm, setAlgorithm] = useState('hybrid')
  const navigate = useNavigate()
  const { addToHistory } = useSearchHistory()

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const searchQuery = params.get('q') || ''
    const algo = params.get('algorithm') || 'hybrid'
    const sort = params.get('sort_by') || 'relevance'
    setQuery(searchQuery)
    setAlgorithm(algo)
    setSortBy(sort)

    if (searchQuery) {
      addToHistory(searchQuery)
      fetchResults(searchQuery, algo, sort)
    }
  }, [])

  const fetchResults = async (searchQuery, algo = 'hybrid', sort = 'relevance') => {
    try {
      setLoading(true)
      const response = await fetch(`/api/search?q=${encodeURIComponent(searchQuery)}&algorithm=${algo}&sort_by=${sort}`)
      const data = await response.json()

      setResults(data.results || [])
      setStats({
        total: data.total_results || 0,
        time: data.time_taken_ms || 0,
        algorithm: data.algorithm || 'HYBRID',
        tokens: data.query_tokens || []
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
      navigate(`/search?q=${encodeURIComponent(newQuery)}&algorithm=${algorithm}&sort_by=${sortBy}`)
    }
  }

  const handleAlgorithmChange = (newAlgo) => {
    setAlgorithm(newAlgo)
    if (query) {
      navigate(`/search?q=${encodeURIComponent(query)}&algorithm=${newAlgo}&sort_by=${sortBy}`)
    }
  }

  const exportResults = () => {
    const dataStr = JSON.stringify(results, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    const exportFileDefaultName = `devseek-results-${query}-${Date.now()}.json`
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }

  return (
    <div className="min-h-screen relative">
      <GridBackground />
      <ParticleBackground count={20} />

      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-between items-center py-6 mb-6"
        >
          <Link to="/" className="flex items-center gap-3 text-white hover:opacity-80 transition-opacity">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
              <Code className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold">Dev<span className="text-blue-400">Seek</span></span>
          </Link>

          <div className="flex items-center gap-3">
            <ThemeToggle />
          </div>
        </motion.header>

        {/* Search Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <AnimatedSearchBar
            onSearch={handleSearch}
            initialQuery={query}
            placeholder="Tìm kiếm..."
          />
        </motion.div>

        {/* Stats & Controls */}
        {!loading && !error && results.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="mb-6"
          >
            <GlassCard className="p-4">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div>
                  <p className="text-white/80">
                    Tìm thấy <span className="font-bold text-white text-lg">{stats.total}</span> kết quả cho
                    <span className="font-bold text-blue-400 mx-1">"{query}"</span>
                    trong <span className="font-bold text-white">{stats.time}ms</span>
                  </p>
                  {stats.tokens && stats.tokens.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {stats.tokens.slice(0, 8).map((token, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 text-xs">
                          {token}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  {/* Algorithm selector */}
                  <div className="flex items-center gap-1 p-1 rounded-full bg-white/5 border border-white/10">
                    {['tfidf', 'bm25', 'hybrid'].map(algo => (
                      <button
                        key={algo}
                        onClick={() => handleAlgorithmChange(algo)}
                        className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                          algorithm === algo
                            ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                            : 'text-white/60 hover:text-white'
                        }`}
                      >
                        {algo.toUpperCase()}
                      </button>
                    ))}
                  </div>

                  {/* View mode */}
                  <div className="flex items-center gap-1 p-1 rounded-full bg-white/5 border border-white/10">
                    <button
                      onClick={() => setViewMode('list')}
                      className={`p-1.5 rounded-full ${viewMode === 'list' ? 'bg-white/10' : ''}`}
                    >
                      <List className="h-4 w-4 text-white" />
                    </button>
                    <button
                      onClick={() => setViewMode('grid')}
                      className={`p-1.5 rounded-full ${viewMode === 'grid' ? 'bg-white/10' : ''}`}
                    >
                      <Grid className="h-4 w-4 text-white" />
                    </button>
                  </div>

                  {/* Export */}
                  <button
                    onClick={exportResults}
                    className="p-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-white/70 hover:text-white transition-colors"
                    title="Xuất kết quả"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        )}

        {/* Loading State */}
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-32"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
              className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full"
            />
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="mt-4 text-white/60"
            >
              Đang tìm kiếm...
            </motion.p>
          </motion.div>
        )}

        {/* Error State */}
        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="py-20"
          >
            <GlassCard className="p-8 text-center max-w-md mx-auto">
              <motion.div
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-16 h-16 mx-auto mb-4 bg-red-500/20 rounded-full flex items-center justify-center"
              >
                <X className="h-8 w-8 text-red-400" />
              </motion.div>
              <h3 className="text-xl font-semibold text-white mb-2">Lỗi tìm kiếm</h3>
              <p className="text-white/60 mb-4">{error}</p>
              <GlassButton onClick={() => fetchResults(query, algorithm, sortBy)} variant="primary">
                <Activity className="h-4 w-4" />
                <span>Thử lại</span>
              </GlassButton>
            </GlassCard>
          </motion.div>
        )}

        {/* Results */}
        {!loading && !error && results.length > 0 && (
          <div className={viewMode === 'grid'
            ? "grid grid-cols-1 lg:grid-cols-2 gap-4"
            : "space-y-4"
          }>
            {results.map((result, index) => (
              <ResultCard
                key={result.id || index}
                result={result}
                query={query}
                index={index}
                viewMode={viewMode}
              />
            ))}
          </div>
        )}

        {/* No Results */}
        {!loading && !error && results.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="py-20"
          >
            <GlassCard className="p-12 text-center max-w-2xl mx-auto">
              <motion.div
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-20 h-20 mx-auto mb-6 bg-blue-500/20 rounded-full flex items-center justify-center"
              >
                <Search className="h-10 w-10 text-blue-400" />
              </motion.div>
              <h3 className="text-2xl font-semibold text-white mb-3">Không tìm thấy kết quả</h3>
              <p className="text-white/60 mb-6">Thử với từ khóa khác hoặc kiểm tra chính tả</p>
              <div className="flex flex-wrap justify-center gap-2">
                {['Python', 'JavaScript', 'React', 'Docker', 'API', 'Algorithm'].map(suggestion => (
                  <motion.button
                    key={suggestion}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleSearch(suggestion)}
                    className="px-4 py-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-white/70 hover:text-white text-sm transition-all"
                  >
                    {suggestion}
                  </motion.button>
                ))}
              </div>
            </GlassCard>
          </motion.div>
        )}
      </div>
    </div>
  )
}

// ============================================================
// ABOUT PAGE
// ============================================================
const AboutPage = () => {
  const navigate = useNavigate()

  const features = [
    { icon: Search, title: 'Tìm kiếm thông minh', description: 'Thuật toán TF-IDF & BM25 tiên tiến', color: 'from-blue-500 to-cyan-500' },
    { icon: Zap, title: 'Siêu nhanh', description: 'Kết quả trong vài mili-giây', color: 'from-yellow-500 to-orange-500' },
    { icon: Sparkles, title: 'AI-Powered', description: 'Ranking thông minh với hybrid algorithm', color: 'from-purple-500 to-pink-500' },
    { icon: Globe, title: 'Đa ngôn ngữ', description: 'Hỗ trợ tiếng Việt và tiếng Anh', color: 'from-green-500 to-emerald-500' },
    { icon: Layers, title: 'B-Tree Indexing', description: 'Truy vấn nhanh với cấu trúc B-Tree', color: 'from-indigo-500 to-purple-500' },
    { icon: BarChart3, title: 'Analytics', description: 'Báo cáo và đánh giá chi tiết', color: 'from-red-500 to-pink-500' },
  ]

  return (
    <div className="min-h-screen relative">
      <GridBackground />
      <ParticleBackground count={20} />

      <div className="relative z-10 container mx-auto px-4 py-8">
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-between items-center py-6 mb-8"
        >
          <Link to="/" className="flex items-center gap-3 text-white hover:opacity-80">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
              <Code className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold">Dev<span className="text-blue-400">Seek</span></span>
          </Link>

          <div className="flex items-center gap-3">
            <ThemeToggle />
          </div>
        </motion.header>

        <main className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-16"
          >
            <h1 className="text-5xl md:text-6xl font-black mb-4 text-white">
              Về <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">DevSeek</span>
            </h1>
            <p className="text-xl text-white/70 max-w-2xl mx-auto">
              Máy tìm kiếm chuyên sâu cho lập trình viên với công nghệ AI tiên tiến
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <GlassCard className="p-6 h-full" glow>
                  <motion.div
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 shadow-lg`}
                  >
                    <feature.icon className="h-6 w-6 text-white" />
                  </motion.div>
                  <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-white/60 text-sm">{feature.description}</p>
                </GlassCard>
              </motion.div>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="text-center"
          >
            <GlassButton onClick={() => navigate('/')} variant="primary">
              <Search className="h-4 w-4" />
              <span>Bắt đầu tìm kiếm ngay</span>
              <ArrowRight className="h-4 w-4" />
            </GlassButton>
          </motion.div>
        </main>
      </div>
    </div>
  )
}

// ============================================================
// SCROLL TO TOP
// ============================================================
const ScrollToTop = () => {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [pathname])
  return null
}

// ============================================================
// ROUTER
// ============================================================
const router = createBrowserRouter([
  { path: '/', element: <><ScrollToTop /><HomePage /></> },
  { path: '/search', element: <><ScrollToTop /><SearchResultsPage /></> },
  { path: '/about', element: <><ScrollToTop /><AboutPage /></> }
])

// ============================================================
// APP
// ============================================================
function App() {
  return (
    <ThemeProvider>
      <RouterProvider router={router} />
    </ThemeProvider>
  )
}

export default App