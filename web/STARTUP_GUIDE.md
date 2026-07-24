# 🚀 DevSeek React App - Quick Start Guide

Follow these simple steps to get the modern React interface running:

## 1️⃣ First Time Setup

```bash
# Navigate to web directory
cd web

# Install dependencies
npm install

# Install Flask (if not already installed)
pip install flask
```

## 2️⃣ Run in Development Mode

**Terminal 1 - Start React Dev Server:**
```bash
npm run dev
```
- This starts Vite on `http://localhost:3000`
- Provides hot reloading and fast refresh

**Terminal 2 - Start Flask Backend:**
```bash
python app.py
```
- This starts Flask on `http://localhost:5000`
- Provides API endpoints for search functionality

**Open your browser:**
👉 [http://localhost:3000](http://localhost:3000)

## 3️⃣ Run in Production Mode

```bash
# Build the React app
npm run build

# Start Flask server
python app.py

# Access the production app
```
👉 [http://localhost:5000/react](http://localhost:5000/react)

## 💡 Tips

- **Dark/Light Mode**: Click the moon/sun icon in the top right to toggle
- **Search**: Type your query and press Enter or click the search button
- **Quick Searches**: Click on suggestion pills for common searches
- **Results**: Click on any result to open the original document

## 🐛 Common Issues & Fixes

**Issue**: `Dynamic require is not supported`
**Fix**: Run `npm install` again to ensure proper dependencies

**Issue**: API not working
**Fix**: Make sure Flask is running on port 5000

**Issue**: Build fails
**Fix**: Delete `node_modules` and run `npm install` again

## 📚 Features to Try

1. **Dark/Light Mode Toggle** - Top right corner
2. **Real-time Search** - Instant results as you type
3. **Query Highlighting** - See your search terms highlighted
4. **Responsive Design** - Works on mobile, tablet, and desktop
5. **Smooth Animations** - Enjoy the liquid glass effects

## 🎨 Customization

Want to change colors or animations?
- Edit `tailwind.config.js` for colors
- Edit `src/index.css` for animations
- Edit `src/App.jsx` for components

Enjoy your modern DevSeek search experience! 🚀