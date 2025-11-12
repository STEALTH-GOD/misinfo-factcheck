# AI Fact Checker Frontend

A modern React frontend for the AI-powered fact-checking application. This interface allows users to submit claims and receive verification results with detailed source analysis.

## Features

- **Modern UI Design**: Clean interface with purple gradient background and responsive design
- **Two-State Interface**:
  - Initial input form for claim submission
  - Results display with comprehensive analysis
- **Real-time Verification**: Connects to the backend API for claim verification
- **Source Analysis**: Displays detailed information about sources used in verification
- **Responsive Design**: Works seamlessly across all device sizes

## Technology Stack

- **React 18**: Modern functional components with hooks
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Lucide React**: Beautiful icon library
- **Inter Font**: Modern typography

## Project Structure

```
src/
├── components/
│   ├── Header.js              # Main application header
│   ├── FactCheckForm.js       # Main form container
│   ├── ClaimInput.js          # Text input for claims
│   ├── VerifyButton.js        # Verification button with loading states
│   ├── ResultsDisplay.js      # Results container
│   ├── StatusBadge.js         # Verdict status display
│   ├── ConfidenceScore.js     # Confidence percentage display
│   ├── MetricsPanel.js        # Three-column metrics display
│   ├── SourceAnalysis.js      # Source analysis container
│   └── SourceCard.js          # Individual source information card
├── App.js                     # Main application component
├── index.js                   # Application entry point
└── index.css                  # Global styles and Tailwind imports
```

## Setup Instructions

1. **Install Dependencies**:

   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**:

   ```bash
   npm start
   ```

3. **Build for Production**:
   ```bash
   npm run build
   ```

## Configuration

The frontend is configured to connect to the backend API at `http://localhost:8000`. Make sure your backend server is running on this port.

### API Integration

The application makes POST requests to `/api/verify_claim` with the following payload:

```json
{
  "claim": "string",
  "lang": "ne"
}
```

## Component Details

### App.js

- Main application state management
- Handles API calls to backend
- Manages loading states and results display

### FactCheckForm

- Contains the claim input and verify button
- Handles form submission
- Manages form states (initial vs results view)

### ResultsDisplay

- Shows verification results
- Displays status badge, confidence score, and metrics
- Contains source analysis section

### StatusBadge

- Color-coded status indicators:
  - **True**: Green with checkmark
  - **False**: Red with X
  - **Mixed Evidence**: Yellow with alert
  - **Unverified**: Gray with info icon

### SourceAnalysis

- Lists all sources used in verification
- Shows sentiment analysis (Supports/Contradicts/Neutral)
- Displays relevance indicators (High/Medium/Low)

## Styling

The application uses a modern design with:

- **Purple gradient background** (#6B7FE8 to #5B6FD8)
- **White content cards** with rounded corners and shadows
- **Responsive grid layouts** for different screen sizes
- **Smooth transitions** and hover effects
- **Color-coded status indicators** for quick visual feedback

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development

To add new features or modify existing ones:

1. Components are modular and reusable
2. State management is handled in the main App component
3. Styling uses Tailwind utility classes
4. Icons are imported from lucide-react

For any issues or feature requests, refer to the main project documentation.
