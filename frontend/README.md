# Krishi Maitri Frontend (Vue.js)

This directory contains the Vue.js frontend for the Krishi Maitri project.

## Getting Started

1. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

2. **Run the development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

3. **Access the app:**
   Open [http://localhost:5173](http://localhost:5173) (or the port shown in your terminal) in your browser.

## Build for Production

```bash
npm run build
# or
yarn build
```

## Notes
- The frontend communicates with the FastAPI backend via REST and WebSocket APIs (see `/backend`).
- Update API URLs in your Vue.js app as needed (e.g., use environment variables for backend base URL).