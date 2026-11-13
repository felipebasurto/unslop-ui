import { Badge } from "./ui";

type Deploy = { id: string; name: string; isLive: boolean };

export function Deploys({ deploys, connection }: { deploys: Deploy[]; connection: { status: "online" | "offline" } }) {
  return (
    <section className="grid gap-6 p-8">
      <div>
        <p className="text-xs font-medium uppercase tracking-widest text-sky-500">Deployments</p>
        <h2 className="text-xl font-semibold">
          🚀 Recent deploys <span className="rounded-full bg-sky-100 px-2 text-xs">NEW</span>
        </h2>
        <p className="text-sm text-slate-500">This section lists your most recent deployments (refreshes automatically).</p>
      </div>
      {connection.status === "online" && (
        <span aria-label="Connected" className="size-2 rounded-full bg-emerald-500" />
      )}
      <ol className="grid gap-2">
        <li><span className="font-mono">01</span> Install the CLI</li>
        <li><span className="font-mono">02</span> Log in</li>
        <li><span className="font-mono">03</span> Deploy</li>
      </ol>
      {deploys.map((deploy) => (
        <article key={deploy.id} className="flex items-center gap-2">
          <h3>{deploy.name}</h3>
          {deploy.isLive && <Badge>Live</Badge>}
          <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-xs">Healthy</span>
        </article>
      ))}
    </section>
  );
}
