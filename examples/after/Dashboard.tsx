import { Card, CardTitle } from "./ui";

export function Dashboard({ revenue, users, churn }: { revenue: number; users: number; churn: number }) {
  return (
    <main className="grid gap-6 p-8">
      <div>
        <h1 className="text-2xl font-semibold">Dashboard</h1>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardTitle>Total revenue</CardTitle>
          <strong>${revenue.toLocaleString()}</strong>
          <span className="text-green-600">+12% vs last month</span>
        </Card>
        <Card>
          <CardTitle>Active users</CardTitle>
          <strong>{users}</strong>
        </Card>
        <Card>
          <CardTitle>Churn</CardTitle>
          <strong>{churn}%</strong>
          <span className="text-xs">Last 30 days</span>
        </Card>
      </div>
    </main>
  );
}
