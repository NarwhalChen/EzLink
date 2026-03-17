import { Link, Route, Routes } from 'react-router-dom';
import { HistoryPage } from './pages/HistoryPage';
import { ReviewPage } from './pages/ReviewPage';
import { SetupPage } from './pages/SetupPage';

export default function App() {
  return (
    <div className="app">
      <h1>EzLink Outreach Agent MVP</h1>
      <nav>
        <Link to="/">Setup</Link> | <Link to="/review">Review</Link> | <Link to="/history">History</Link>
      </nav>
      <Routes>
        <Route path="/" element={<SetupPage />} />
        <Route path="/review" element={<ReviewPage />} />
        <Route path="/history" element={<HistoryPage />} />
      </Routes>
    </div>
  );
}
