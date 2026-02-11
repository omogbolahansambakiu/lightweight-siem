// App.jsx - Main SIEM Dashboard Application

import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const App = () => {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({
    total_alerts: 0,
    critical_alerts: 0,
    events_per_sec: 0,
    failed_logins: 0,
    timeline: [],
    by_severity: [],
    top_ips: [],
    auth_events: []
  });
  const [timeRange, setTimeRange] = useState('24h');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/dashboard?range=${timeRange}`);
      
      if (!response.ok) {
        console.warn('API not available, using mock data');
        setStats(getMockStats());
        setAlerts(getMockAlerts());
        setError('Using demo data - API endpoint not available');
      } else {
        const data = await response.json();
        setAlerts(data.alerts || getMockAlerts());
        setStats({
          total_alerts: data.stats?.total_alerts || 0,
          critical_alerts: data.stats?.critical_alerts || 0,
          events_per_sec: data.stats?.events_per_sec || 0,
          failed_logins: data.stats?.failed_logins || 0,
          timeline: data.stats?.timeline || getMockStats().timeline,
          by_severity: data.stats?.by_severity || getMockStats().by_severity,
          top_ips: data.stats?.top_ips || getMockStats().top_ips,
          auth_events: data.stats?.auth_events || getMockStats().auth_events
        });
        setError(null);
      }
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setStats(getMockStats());
      setAlerts(getMockAlerts());
      setError('Using demo data - API connection failed');
    } finally {
      setLoading(false);
    }
  };

  const getMockStats = () => ({
    total_alerts: 42,
    critical_alerts: 8,
    events_per_sec: 127,
    failed_logins: 156,
    timeline: [
      { time: '00:00', critical: 2, high: 5, medium: 8 },
      { time: '04:00', critical: 1, high: 3, medium: 12 },
      { time: '08:00', critical: 3, high: 7, medium: 15 },
      { time: '12:00', critical: 5, high: 9, medium: 18 },
      { time: '16:00', critical: 4, high: 6, medium: 14 },
      { time: '20:00', critical: 2, high: 4, medium: 10 }
    ],
    by_severity: [
      { severity: 'critical', count: 8 },
      { severity: 'high', count: 15 },
      { severity: 'medium', count: 12 },
      { severity: 'low', count: 7 }
    ],
    top_ips: [
      { ip: '192.168.1.100', count: 45 },
      { ip: '10.0.0.25', count: 32 },
      { ip: '172.16.0.50', count: 28 },
      { ip: '192.168.1.75', count: 19 },
      { ip: '10.0.0.100', count: 15 }
    ],
    auth_events: [
      { hour: '00:00', failed: 5, success: 120 },
      { hour: '04:00', failed: 3, success: 45 },
      { hour: '08:00', failed: 12, success: 250 },
      { hour: '12:00', failed: 8, success: 310 },
      { hour: '16:00', failed: 15, success: 280 },
      { hour: '20:00', failed: 7, success: 190 }
    ]
  });

  const getMockAlerts = () => [
    {
      alert_id: '1',
      timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
      rule_name: 'Multiple Failed Login Attempts',
      severity: 'critical',
      evidence: { source_ip: '192.168.1.100', user: 'admin' }
    },
    {
      alert_id: '2',
      timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
      rule_name: 'Suspicious Port Scan Detected',
      severity: 'high',
      evidence: { source_ip: '10.0.0.25', user: 'N/A' }
    },
    {
      alert_id: '3',
      timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
      rule_name: 'Unusual Outbound Traffic',
      severity: 'medium',
      evidence: { source_ip: '172.16.0.50', user: 'service_account' }
    },
    {
      alert_id: '4',
      timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
      rule_name: 'Unauthorized Access Attempt',
      severity: 'high',
      evidence: { source_ip: '192.168.1.75', user: 'guest' }
    },
    {
      alert_id: '5',
      timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
      rule_name: 'Config File Modified',
      severity: 'low',
      evidence: { source_ip: '10.0.0.100', user: 'root' }
    }
  ];

  const SEVERITY_COLORS = {
    critical: '#d32f2f',
    high: '#f57c00',
    medium: '#fbc02d',
    low: '#7cb342'
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">SIEM Dashboard</h1>
            {error && (
              <p className="text-sm text-orange-600 mt-1">⚠️ {error}</p>
            )}
            {loading && (
              <p className="text-sm text-blue-600 mt-1">Loading...</p>
            )}
          </div>
          <select 
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <MetricCard 
            title="Total Alerts"
            value={stats.total_alerts}
            change="+12%"
            color="blue"
          />
          <MetricCard 
            title="Critical Alerts"
            value={stats.critical_alerts}
            change="+5"
            color="red"
          />
          <MetricCard 
            title="Events/Second"
            value={stats.events_per_sec}
            change="Normal"
            color="green"
          />
          <MetricCard 
            title="Failed Logins"
            value={stats.failed_logins}
            change="+23%"
            color="yellow"
          />
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          
          {/* Alert Timeline */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Alert Timeline</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={stats.timeline}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="critical" stroke="#d32f2f" strokeWidth={2} />
                <Line type="monotone" dataKey="high" stroke="#f57c00" strokeWidth={2} />
                <Line type="monotone" dataKey="medium" stroke="#fbc02d" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Severity Distribution */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Alerts by Severity</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stats.by_severity}
                  dataKey="count"
                  nameKey="severity"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label
                >
                  {stats.by_severity?.map((entry, index) => (
                    <Cell key={index} fill={SEVERITY_COLORS[entry.severity]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          
          {/* Top Source IPs */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Top Source IPs</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.top_ips}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="ip" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#1976d2" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Failed vs Successful Logins */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Authentication Events</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.auth_events}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="failed" stackId="a" fill="#d32f2f" />
                <Bar dataKey="success" stackId="a" fill="#7cb342" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Alerts Table */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Recent Alerts</h2>
          <AlertsTable alerts={alerts} />
        </div>

      </div>
    </div>
  );
};

const MetricCard = ({ title, value, change, color }) => {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-800',
    red: 'bg-red-100 text-red-800',
    green: 'bg-green-100 text-green-800',
    yellow: 'bg-yellow-100 text-yellow-800'
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
      <div className="text-sm text-gray-600 mb-1">{title}</div>
      <div className="text-3xl font-bold text-gray-900">{value || 0}</div>
      <div className={`text-sm mt-2 px-2 py-1 rounded inline-block ${colorClasses[color]}`}>
        {change}
      </div>
    </div>
  );
};

const AlertsTable = ({ alerts }) => {
  const severityBadge = (severity) => {
    const classes = {
      critical: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800'
    };
    
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${classes[severity]}`}>
        {severity?.toUpperCase() || 'UNKNOWN'}
      </span>
    );
  };

  if (!alerts || alerts.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No alerts to display
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rule</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {alerts.map((alert) => (
            <tr key={alert.alert_id} className="hover:bg-gray-50 transition-colors">
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {new Date(alert.timestamp).toLocaleString()}
              </td>
              <td className="px-6 py-4 text-sm text-gray-900">{alert.rule_name}</td>
              <td className="px-6 py-4 whitespace-nowrap">{severityBadge(alert.severity)}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                {alert.evidence?.source_ip || 'N/A'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {alert.evidence?.user || 'N/A'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                <button className="text-blue-600 hover:text-blue-900 mr-3 font-medium">Investigate</button>
                <button className="text-green-600 hover:text-green-900 font-medium">Resolve</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default App;