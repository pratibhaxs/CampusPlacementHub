import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { fetchAdminStatistics } from "../../api/statsApi";

export default function Statistics() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchAdminStatistics().then((res) => setStats(res.data));
  }, []);

  if (!stats) return <div className="page"><p>Loading...</p></div>;

  const companyChartData = stats.most_discussed_companies.map((c) => ({ name: c.company, value: c.count }));
  const topicChartData = stats.most_frequent_topics.map((t) => ({ name: t.topic, value: t.count }));

  return (
    <div className="page">
      <h2>Platform Statistics</h2>

      <div className="stats-cards">
        <div className="stat-card"><span className="stat-value">{stats.total_students}</span><span className="stat-label">Students</span></div>
        <div className="stat-card"><span className="stat-value">{stats.total_alumni}</span><span className="stat-label">Alumni</span></div>
        <div className="stat-card"><span className="stat-value">{stats.total_companies}</span><span className="stat-label">Companies</span></div>
        <div className="stat-card"><span className="stat-value">{stats.total_experiences}</span><span className="stat-label">Approved experiences</span></div>
        <div className="stat-card"><span className="stat-value">{stats.pending_experiences}</span><span className="stat-label">Pending approval</span></div>
      </div>

      <div className="repo-layout">
        <div>
          <h3>Most Discussed Companies</h3>
          {companyChartData.length === 0 ? (
            <p className="hint">No approved experiences yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={Math.max(160, companyChartData.length * 40)}>
              <BarChart data={companyChartData} layout="vertical" margin={{ left: 20, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" allowDecimals={false} />
                <YAxis type="category" dataKey="name" width={130} />
                <Tooltip />
                <Bar dataKey="value" fill="#2f5fdb" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div>
          <h3>🔥 Most Frequent Topics</h3>
          {topicChartData.length === 0 ? (
            <p className="hint">No approved experiences yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={Math.max(160, topicChartData.length * 40)}>
              <BarChart data={topicChartData} layout="vertical" margin={{ left: 20, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" allowDecimals={false} />
                <YAxis type="category" dataKey="name" width={110} />
                <Tooltip />
                <Bar dataKey="value" fill="#e6a817" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}
