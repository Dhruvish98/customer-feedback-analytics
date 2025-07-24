// frontend/src/App.js - Complete version with all routes
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  RadialLinearScale
} from 'chart.js';
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Layout/Navbar';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Dashboard from './components/Dashboard/Dashboard';
import UserDashboard from './components/UserDashboard/UserDashboard';
import ReviewForm from './components/ReviewForm/ReviewForm';
import ReviewHistory from './components/ReviewHistory/ReviewHistory';
import AdminPanel from './components/Admin/AdminPanel';
import ProductAnalytics from './components/Analytics/ProductAnalytics';
import CategoryAnalytics from './components/Analytics/CategoryAnalytics';
import RealTimeMonitor from './components/Dashboard/RealTimeMonitor';
import AspectAnalysis from './components/Analytics/AspectAnalysis';
import CompetitorIntelligence from './components/Analytics/CompetitorIntelligence';
import PredictiveAnalytics from './components/Analytics/PredictiveAnalytics';
import './App.css';

// Register all components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  RadialLinearScale
);

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <div className="app">
            <Navbar />
            <main className="main-content">
              <Routes>
                {/* Auth Routes */}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                
                {/* User Dashboard Routes */}
                <Route 
                  path="/dashboard" 
                  element={
                    <ProtectedRoute>
                      <Dashboard />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/user-dashboard" 
                  element={
                    <ProtectedRoute>
                      <UserDashboard />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/monitor" 
                  element={
                    <ProtectedRoute>
                      <RealTimeMonitor />
                    </ProtectedRoute>
                  } 
                />
                
                {/* Review Routes */}
                <Route 
                  path="/submit-review" 
                  element={
                    <ProtectedRoute>
                      <ReviewForm />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/review-history" 
                  element={
                    <ProtectedRoute>
                      <ReviewHistory />
                    </ProtectedRoute>
                  } 
                />
                
                {/* Analytics Routes - Routes without parameters FIRST */}
                <Route 
                  path="/analytics/aspects" 
                  element={
                    <ProtectedRoute>
                      <AspectAnalysis />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/analytics/competitors" 
                  element={
                    <ProtectedRoute>
                      <CompetitorIntelligence />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/analytics/predictions" 
                  element={
                    <ProtectedRoute>
                      <PredictiveAnalytics />
                    </ProtectedRoute>
                  } 
                />
                
                {/* Analytics Routes - Routes with parameters SECOND */}
                <Route 
                  path="/analytics/product/:productId" 
                  element={
                    <ProtectedRoute>
                      <ProductAnalytics />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/analytics/category/:category" 
                  element={
                    <ProtectedRoute>
                      <CategoryAnalytics />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/analytics/aspects/:productId" 
                  element={
                    <ProtectedRoute>
                      <AspectAnalysis />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/analytics/competitors/:productId" 
                  element={
                    <ProtectedRoute>
                      <CompetitorIntelligence />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/analytics/predictions/:productId" 
                  element={
                    <ProtectedRoute>
                      <PredictiveAnalytics />
                    </ProtectedRoute>
                  } 
                />
                
                {/* Admin Routes */}
                <Route 
                  path="/admin" 
                  element={
                    <ProtectedRoute requireAdmin>
                      <AdminPanel />
                    </ProtectedRoute>
                  } 
                />
                
                {/* Default Route - redirect based on user role */}
                <Route 
                  path="/" 
                  element={
                    <ProtectedRoute>
                      <Navigate to="/dashboard" replace />
                    </ProtectedRoute>
                  } 
                />
                
                {/* Catch all route for 404 */}
                <Route 
                  path="*" 
                  element={
                    <div className="not-found">
                      <h2>404 - Page Not Found</h2>
                      <p>The page you're looking for doesn't exist.</p>
                      <Navigate to="/dashboard" replace />
                    </div>
                  } 
                />
              </Routes>
            </main>
          </div>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;