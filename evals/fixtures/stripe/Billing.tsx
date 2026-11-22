export function Billing({ plans, failed }) {
  return (
    <section>
      {plans.map((plan) => (
        <article
          key={plan.id}
          className="relative overflow-hidden rounded-xl border-l-4 border-indigo-500 bg-white p-5"
        >
          <span className="absolute inset-y-0 left-0 w-1 bg-fuchsia-500" />
          <h3>{plan.name}</h3>
          <p className="text-sm text-muted-foreground">{plan.blurb}</p>
          <a href={plan.href} className="mt-2 inline-block">
            Choose {plan.name}
          </a>
        </article>
      ))}
      {failed && (
        <div role="alert" className="rounded-lg border-l-4 border-red-500 bg-red-50 p-4">
          Payment failed
        </div>
      )}
    </section>
  );
}
