# DevSeek React Web Interface 🚀

Modern React-based web interface for DevSeek search engine with liquid glass effects, dark/light mode, framer-motion animations, and optimized performance.

## ✨ Features

### Core Features
- 🎨 **Modern UI** with liquid glass effects and framer-motion animations
- 🌓 **Dark/Light Mode** toggle with local storage persistence
- 📱 **Responsive Design** for all device sizes
- ⚡ **Optimized Performance** with Vite and code splitting
- 🔍 **Smart Search** with query highlighting using backend HTML
- 🎯 **Real-time Results** with smooth transitions

### Advanced Features
- ✨ **Particle Background** - Animated floating particles
- 🌊 **Liquid Glass Effects** - Advanced glassmorphism with backdrop filters
- 🎭 **Framer Motion Animations** - Smooth spring animations and transitions
- 💫 **Animated Score Circles** - SVG circular progress indicators
- 🎨 **Gradient Animations** - Animated gradient text and backgrounds
- 🔥 **Cmd+K Shortcut** - Quick search keyboard shortcut
- 📊 **Search History** - Persistent localStorage history
- 🎯 **Multiple Algorithms** - TF-IDF, BM25, Hybrid switching
- 📱 **Grid/List View** - Toggle between view modes
- 💾 **Export Results** - Download as JSON
- ⭐ **Bookmark & Share** - Save and share results
- 🎨 **Animated Grid Background** - Cyberpunk-style grid overlay
- 🌟 **Hover Effects** - Smooth lift, glow, and scale animations
- 📈 **Statistics Cards** - Animated stats with delays
- 🎪 **Ripple Effects** - Interactive button feedback

## 🛠️ Tech Stack

- **React 18** - UI framework
- **Vite 5** - Build tool and dev server
- **Framer Motion** - Animation library
- **React Router 6** - Client-side routing
- **Tailwind CSS 3** - Utility-first CSS
- **Lucide React** - Beautiful vector icons
- **ESBuild** - Fast minification

## 📋 Prerequisites

- Node.js v18+ (recommended v20+)
- npm v9+ or yarn
- Python 3.8+

## 🛠️ Installation

```bash
cd web
npm install
```

## 🚀 Running the Application

### Development Mode (Recommended)

**Terminal 1 - Start Vite dev server:**
```bash
npm run dev
```
Access at: `http://localhost:3000`

**Terminal 2 - Start Flask backend:**
```bash
python app.py
```

### Production Mode

```bash
npm run build
python app.py
```
Access at: `http://localhost:5000/react`

## 🎨 Key Components

### 🎭 Animations
- Page transitions with fade/slide
- Staggered animations on lists
- Hover effects with scale/glow
- Loading states with spinners
- Score circles with animated SVG
- Particle background effects

### 🌊 Liquid Glass Effects
- Backdrop blur on all cards
- Gradient borders on hover
- Smooth glass transitions
- Multi-layer glassmorphism

### 🔍 Search Features
- **Query Highlighting** - Backend returns HTML with `<mark>` tags
- **Multiple Algorithms** - Switch between TF-IDF/BM25/Hybrid
- **View Modes** - Grid or list view
- **Export Results** - Download as JSON
- **Search History** - LocalStorage persistence

## 📁 Project Structure

```
web/
├── src/
│   ├── App.jsx           # Main application
│   ├── main.jsx          # Entry point
│   └── index.css         # Global styles
├── vite.config.js        # Vite configuration
├── tailwind.config.js    # Tailwind configuration
├── package.json          # Dependencies
└── index.html            # HTML entry
```

## 🎯 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search` | GET | Search with algorithm parameter |
| `/api/stats` | GET | System statistics |
| `/api/evaluate` | GET | Evaluation metrics |

## 🎨 Customization

### Change Theme Colors
Edit `tailwind.config.js` and `index.css`

### Modify Animations
Edit Framer Motion props in `App.jsx`

### Add New Features
Components are modular and easy to extend

## 🐛 Troubleshooting

- **Build fails**: Delete `node_modules` and run `npm install`
- **Animations laggy**: Reduce particle count in `App.jsx`
- **Mark tags not highlighted**: Check `index.css` for `mark` styles

## 📄 License

MIT License