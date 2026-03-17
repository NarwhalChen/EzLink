import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import SetupPage from "./pages/SetupPage";
import ReviewPage from "./pages/ReviewPage";
import HistoryPage from "./pages/HistoryPage";
import "./styles/app.css";

export default function App() {
  return (
    <BrowserRouter>
      <nav className="nav">
        <div className="nav-inner">
          <NavLink to="/" className="nav-brand">
            🔗 EzLink
          </NavLink>
          <ul className="nav-links">
            <li>
              <NavLink
                to="/"
                end
                className={({ isActive }) => (isActive ? "active" : "")}
              >
                Setup
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/review"
                className={({ isActive }) => (isActive ? "active" : "")}
              >
                Review
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/history"
                className={({ isActive }) => (isActive ? "active" : "")}
              >
                History
              </NavLink>
            </li>
          </ul>
        </div>
      </nav>

      <main>
        <Routes>
          <Route path="/" element={<SetupPage />} />
          <Route path="/review" element={<ReviewPage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
