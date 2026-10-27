# Before and after

## Contents
- Hero with eyebrow (U1, U3, U8)
- Numbered feature section (U2, U4)
- Card that explains itself (U4, U5)
- Status line (U6, U10)
- KPI tile (U11, U14)
- Chart header (U12, U13)
- Form field (U7)

## Hero with eyebrow (U1, U3, U8)

Before:
```html
<p class="text-xs uppercase tracking-widest text-indigo-500">Introducing Ledger</p>
<h1>Finance. Simplified. Finally.</h1>
<p>The all-in-one platform that helps modern teams seamlessly manage their money — without the hassle.</p>
```

After:
```html
<h1>Ledger tracks every company card in one place</h1>
<p>Receipts match to transactions automatically.</p>
```

The eyebrow goes (U1). The staccato slogan becomes a sentence that says what the product does (U8). The subtitle keeps one concrete fact and loses "seamlessly", "all-in-one" and the em dash (unslop 7, 13).

## Numbered feature section (U2, U4)

Before:
```jsx
<span className="font-mono text-sm">01 //</span>
<h3>Smart sync</h3>
<p>Our smart sync feature automatically keeps your files in sync across all of your devices.</p>
```

After:
```jsx
<h3>Sync across devices</h3>
<p>Edits on your phone show up on your laptop within seconds.</p>
```

The order of features isn't real, so the number goes (U2). The description repeated the title, so it now states a fact the title doesn't (U4).

## Card that explains itself (U4, U5)

Before:
```jsx
<Card>
  <CardTitle>Recent activity</CardTitle>
  <CardDescription>This card shows your most recent activity across the workspace (updates in real time).</CardDescription>
  <ActivityList />
</Card>
```

After:
```jsx
<Card>
  <CardTitle>Recent activity</CardTitle>
  <ActivityList />
</Card>
```

## Status line (U6, U10)

Before:
```jsx
<div className="flex items-center gap-2 text-xs">
  <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
  Live · 3 agents · Synced · v2.4.1 · Updated just now
</div>
```

After, when nothing in the app tracks a live connection:
```jsx
<p className="text-xs">3 agents</p>
```

If the dot is bound to a real websocket state, keep the dot with an `aria-label` and drop the word "Live".

## KPI tile (U11, U14)

Before:
```jsx
<Tile>
  <span>💰 Total revenue</span>
  <strong>$48,200</strong>
  <span className="text-green-600">▲ 12% up</span>
  <p>Revenue grew 12% compared to last month, showing strong momentum.</p>
</Tile>
```

After:
```jsx
<Tile>
  <span>Revenue</span>
  <strong>$48,200</strong>
  <span className="text-green-600">▲ 12% vs last month</span>
</Tile>
```

## Chart header (U12, U13)

Before:
```js
title: { text: 'Line chart of weekly active users' },
subtitle: { text: 'Each point represents one week. Hover over a point to see the exact value.' },
legend: { display: true }, // single series
```

After:
```js
title: { text: 'Weekly active users' },
legend: { display: false },
```

## Form field (U7)

Before:
```html
<label>Email address</label>
<input placeholder="Enter your email address" />
<small>We'll use this email address to contact you.</small>
```

After:
```html
<label for="email">Email</label>
<input id="email" type="email" />
```
