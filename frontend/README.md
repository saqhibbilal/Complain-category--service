# Complaint Categorization Frontend

Modern React + TypeScript frontend for the Complaint Categorization and RAG System.

## Features

- **Complaint Submission**: Submit new complaints with optional metadata
- **AI Categorization**: View AI-generated categories and summaries
- **Similar Complaints**: See similar complaints with similarity scores
- **Modern UI**: Clean, sharp design with Quantico font
- **Responsive**: Works on desktop and mobile devices

## Tech Stack

- React 18
- TypeScript
- Vite
- Axios for API calls
- CSS3 with custom properties

## Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

4. **Preview production build:**
   ```bash
   npm run preview
   ```

## Configuration

The frontend is configured to proxy API requests to `http://localhost:8000` (backend). This is configured in `vite.config.ts`.

To change the backend URL, update the proxy target in `vite.config.ts`:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',  // Change this
    changeOrigin: true,
  },
}
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ComplaintSubmissionForm.tsx
│   │   ├── ComplaintResults.tsx
│   │   └── SimilarComplaintsList.tsx
│   ├── services/            # API services
│   │   └── api.ts
│   ├── App.tsx              # Main app component
│   ├── App.css              # App styles
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Usage

1. Start the backend server (port 8000)
2. Start the frontend dev server (port 5173)
3. Open `http://localhost:5173` in your browser
4. Submit a complaint and view the results

## Design

- **Font**: Quantico (Google Fonts)
- **Color Scheme**: Blue primary, clean grays
- **Style**: Modern, sharp, minimal
- **Components**: Card-based layout with subtle shadows and borders
