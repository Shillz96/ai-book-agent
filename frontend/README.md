# Human-in-the-Loop Dashboard

A React application with Firebase integration for managing AI book marketing automation with human oversight.

## 🚀 Quick Start

### Prerequisites

- Node.js (version 14 or higher)
- npm or yarn package manager
- Firebase project (for configuration)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure Firebase (see Configuration section below)

3. Start the development server:
```bash
npm start
```

The application will open at `http://localhost:3000`

## 🔧 Configuration

### Firebase Setup

Before running the application, you need to configure Firebase by setting global variables. There are several ways to do this:

#### Method 1: Direct Script Injection

Edit `public/index.html` and replace the Firebase configuration:

```javascript
window.__firebase_config = JSON.stringify({
  apiKey: "your-api-key",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "your-app-id"
});
```

#### Method 2: Environment Variables (Build Process)

You can inject these values during build time or via server-side rendering:

- `window.__app_id` - Your application identifier
- `window.__firebase_config` - JSON string of Firebase configuration
- `window.__initial_auth_token` - Optional initial authentication token
- `window.__debug_mode` - Set to `true` for detailed console logging

### Required Firebase Services

Make sure your Firebase project has these services enabled:
- **Authentication** (Anonymous sign-in enabled)
- **Firestore Database** (with appropriate security rules)

## 📱 Features

### ✅ Implemented Features

- **Firebase Integration**: Complete setup with App, Auth, and Firestore
- **Authentication**: Supports both custom tokens and anonymous sign-in
- **Error Handling**: User-friendly error messages via modal system
- **Loading States**: Beautiful loading animations during initialization
- **Responsive Design**: Mobile-friendly UI with Tailwind CSS
- **Context Management**: Firebase services available throughout the app
- **PWA Ready**: Progressive Web App capabilities

### 🔄 Authentication Flow

1. **Initialization**: App attempts to parse Firebase configuration
2. **Validation**: Checks if configuration is valid and complete
3. **Service Setup**: Initializes Firebase App, Auth, and Firestore
4. **Authentication**: 
   - Uses custom token if `__initial_auth_token` is provided
   - Falls back to anonymous sign-in if no token is available
5. **State Management**: Maintains authentication state throughout the app

### 🎨 UI Components

- **Loading Screen**: Animated spinner with status messages
- **Dashboard Header**: User info and sign-out functionality
- **Status Cards**: Firebase connection status and service health
- **Modal System**: Error and informational messages
- **Responsive Layout**: Works on desktop, tablet, and mobile devices

## 🔍 Debugging

### Enable Debug Mode

Set debug mode in `index.html`:
```javascript
window.__debug_mode = true;
```

This will enable:
- Detailed console logging
- Performance measurements
- Configuration validation messages

### Common Issues

1. **"Firebase configuration is missing"**
   - Ensure `__firebase_config` is properly set
   - Check that the JSON is valid
   - Verify Firebase project settings

2. **Authentication failures**
   - Check if Anonymous sign-in is enabled in Firebase Console
   - Verify custom token format if using `__initial_auth_token`
   - Review Firebase Authentication settings

3. **Firestore connection issues**
   - Verify Firestore is enabled for your project
   - Check database security rules
   - Ensure project ID matches configuration

## 📂 Project Structure

```
frontend/
├── public/
│   ├── index.html          # HTML template with global variables
│   ├── manifest.json       # PWA manifest
│   └── favicon.ico         # Application icon
├── src/
│   ├── App.js             # Main React component
│   ├── index.js           # React entry point
│   └── index.css          # Tailwind CSS styles
├── package.json           # Dependencies and scripts
└── README.md             # This file
```

## 🛠 Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Create production build
- `npm test` - Run test suite
- `npm eject` - Eject from create-react-app (irreversible)

### Code Style

The application follows these principles:
- **Clean, modular code** with extensive comments
- **React functional components** with hooks
- **Tailwind CSS** for styling
- **Error boundaries** and proper error handling
- **Accessibility** considerations throughout

### State Management

The app uses React's built-in state management:
- `useState` for local component state
- `useEffect` for side effects and lifecycle management
- `createContext` for sharing Firebase services
- `useContext` for accessing shared state

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

This creates a `build/` directory with optimized files for production.

### Environment Variables

For production deployment, ensure these variables are properly injected:

```javascript
// Required
window.__firebase_config = "JSON string of Firebase config";

// Optional
window.__app_id = "your-app-identifier";
window.__initial_auth_token = "custom-auth-token";
window.__debug_mode = false; // Set to false in production
```

## 📝 Next Steps

This implementation provides the foundation for the Human-in-the-Loop Dashboard. You can extend it by:

1. **Adding more components** for specific dashboard functionality
2. **Implementing Firestore operations** for data management
3. **Creating user management** features
4. **Adding real-time listeners** for live data updates
5. **Implementing routing** for multiple pages
6. **Adding book settings management**
7. **Creating post management interfaces**

## 🤝 Contributing

When contributing to this project:
1. Follow the existing code style and commenting patterns
2. Test all Firebase integration thoroughly
3. Ensure responsive design works on all devices
4. Add appropriate error handling for new features
5. Update this README with any new configuration requirements

## 📄 License

This project is part of the AI Book Agent system for managing book marketing automation. 