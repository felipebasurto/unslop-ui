export function Pricing({ plans }) {
  return (
    <section className="grid grid-cols-2 gap-[7px] mt-[13px] p-6">
      {plans.map((plan) => (
        <div
          key={plan.id}
          className="rounded-lg bg-gradient-to-r from-indigo-500 to-purple-500 shadow-[0_0_20px_rgba(139,92,246,0.5)] p-6"
        >
          <h2 className="text-2xl font-black bg-gradient-to-r from-indigo-600 to-pink-500 bg-clip-text text-transparent">
            {plan.name}
          </h2>
          <p className="text-3xl font-extrabold">{plan.price}</p>
          <a href={plan.href} className="inline-block rounded border px-4 py-2 shadow-sm">
            Choose {plan.name}
          </a>
        </div>
      ))}
    </section>
  );
}
