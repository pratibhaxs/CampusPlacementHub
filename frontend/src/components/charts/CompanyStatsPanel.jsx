import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { fetchCompanyStats } from "../../api/statsApi";

export default function CompanyStatsPanel({ companyId }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchCompanyStats(companyId).then((res) => setStats(res.data));
  }, [companyId]);

  if (!stats) return <p className="hint">Loading...</p>;
  if (stats.total_experiences === 0) {
    return <p className="hint">Not enough approved experiences yet to show analytics.</p>;
  }

  const chartData = stats.topic_percentages.map((t) => ({ name: t.topic, value: t.percentage }));

  return (
    <div className="stats-panel">
      <div className="stats-cards">
        <div className="stat-card">
          <span className="stat-value">{stats.total_experiences}</span>
          <span className="stat-label">Total experiences</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{stats.average_rounds}</span>
          <span className="stat-label">Average rounds</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{stats.most_common_first_round || "—"}</span>
          <span className="stat-label">Most common first round</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{stats.average_difficulty || "—"}</span>
          <span className="stat-label">Average difficulty</span>
        </div>
      </div>

      {chartData.length > 0 && (
        <>
          <h4>Most common technical topics</h4>
          <ResponsiveContainer width="100%" height={Math.max(180, chartData.length * 36)}>
            <BarChart data={chartData} layout="vertical" margin={{ left: 20, right: 20 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
              <YAxis type="category" dataKey="name" width={110} />
              <Tooltip formatter={(v) => `${v}%`} />
              <Bar dataKey="value" fill="#2f5fdb" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  );
}
