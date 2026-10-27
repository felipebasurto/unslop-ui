import { Card, CardTitle, CardDescription } from "./ui";

export function Dashboard({ revenue, users, churn }: { revenue: number; users: number; churn: number }) {
  return (
    <main className="grid gap-6 p-8">
      <div>
        <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-muted-foreground">Overview</p>
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <p className="text-muted-foreground">A real-time overview of your key business metrics, all in one place.</p>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardTitle>💰 Total revenue</CardTitle>
          <strong>${revenue.toLocaleString()}</strong>
          <span className="text-green-600">▲ 12% up</span>
          <CardDescription>Revenue grew 12% compared to last month, showing strong momentum.</CardDescription>
        </Card>
        <Card>
          <CardTitle>👥 Active users</CardTitle>
          <strong>{users}</strong>
          <span className="flex items-center gap-1 text-xs"><span className="size-2 rounded-full bg-emerald-500 animate-ping" />Live</span>
          <CardDescription>This card shows the number of users active right now (updates in real time).</CardDescription>
        </Card>
        <Card>
          <CardTitle>📉 Churn</CardTitle>
          <strong>{churn}%</strong>
          <span className="text-xs">Last 30 days · All plans · Excl. trials</span>
        </Card>
      </div>
    </main>
  );
}
