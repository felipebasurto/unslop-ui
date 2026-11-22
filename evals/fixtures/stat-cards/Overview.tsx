export function Overview({ stats }) {
  return (
    <div>
      <h1>Overview</h1>
      <div className="grid grid-cols-3 gap-4">
        <Card><p className="text-3xl">{stats.users}</p><p>Users</p></Card>
        <Card><p className="text-3xl">{stats.revenue}</p><p>Revenue</p></Card>
        <Card><p className="text-3xl">{stats.churn}</p><p>Churn</p></Card>
      </div>
    </div>
  );
}
