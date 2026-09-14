import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export default function StudentDashboard() {
  const { user } = useAuth();
  return (
    <div className="page">
      <h2>Welcome, {user?.name}</h2>
      <p className="hint">{user?.college_name}{user?.branch && ` · ${user.branch}`}</p>

      <div className="dashboard-cards">
        <Link to="/search" className="dashboard-card">
          <h3>Search Experiences</h3>
          <p>Filter by company, college, role, year, branch, difficulty, or topic.</p>
        </Link>
        <Link to="/companies" className="dashboard-card">
          <h3>Browse Companies</h3>
          <p>See placement stats, recommended prep, and shared experiences.</p>
        </Link>
        <Link to="/questions" className="dashboard-card">
          <h3>Question Repository</h3>
          <p>Browse interview questions with frequency and difficulty.</p>
        </Link>
        <Link to="/student/saved" className="dashboard-card">
          <h3>Saved Items</h3>
          <p>Everything you've bookmarked, in one place.</p>
        </Link>
      </div>
    </div>
  );
}
