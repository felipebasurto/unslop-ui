export function PricingStats({ matched, total, spend, delta }) {
  return (
    <main className="grid gap-8 p-8">
      <section>
        <h1>Kestrel</h1>
        <p>Track team expenses across cards and invoices.</p>
        <a href="/signup">Start free trial</a>
        <p className="text-xs text-slate-500">No credit card required · Cancel anytime</p>
      </section>

      <section className="grid grid-cols-2 gap-4">
        <div className="rounded border p-4">
          <p>Receipts matched</p>
          <strong>{matched} / {total}</strong>
          <p className="text-xs">98.7% matched automatically</p>
          <p className="text-xs">19 remaining in queue</p>
        </div>
        <div className="rounded border p-4">
          <p>Monthly spend</p>
          <strong>{spend}</strong>
          <p className="text-xs">{delta} vs last month</p>
        </div>
      </section>

      <section className="grid grid-cols-2 gap-4">
        <div>
          <h2>Growth</h2>
          <p>Up to 25 seats, email support.</p>
        </div>
        <div>
          <h2>Scale</h2>
          <p>Unlimited seats, SSO and audit log.</p>
        </div>
      </section>

      <form>
        <label htmlFor="email">Work email</label>
        <input id="email" type="email" placeholder="you@company.com" />
        <button type="submit">Join waitlist</button>
        <p className="text-xs text-slate-500">No spam, unsubscribe anytime.</p>
      </form>
    </main>
  );
}
