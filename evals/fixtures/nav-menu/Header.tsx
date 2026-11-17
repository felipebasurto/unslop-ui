import { Compass, Menu as MenuIcon, Mountain, Snowflake, Waves } from "lucide-react";
import { Dropdown } from "./ui";

const destinations = [
  { name: "Svalbard", blurb: "Explore the Arctic's crown jewel", href: "/svalbard", Icon: Mountain },
  { name: "Greenland", blurb: "Discover majestic ice fjords", href: "/greenland", Icon: Compass },
  { name: "Iceland", blurb: "The land of fire and ice", href: "/iceland", Icon: Waves },
  { name: "Antarctica", blurb: "The last great wilderness", href: "/antarctica", Icon: Snowflake },
];

export function Header() {
  return (
    <header className="p-6">
      <nav className="flex items-center gap-6">
        <a href="/voyages">Voyages</a>
        <Dropdown label="Destinations">
          <p className="text-xs font-medium uppercase tracking-widest text-slate-500">Popular destinations</p>
          <ul className="grid gap-1">
            {destinations.map(({ name, blurb, href, Icon }) => (
              <li key={name}>
                <a href={href} className="flex items-center gap-3">
                  <span className="grid size-10 place-items-center rounded-lg bg-sky-100">
                    <Icon className="size-4" />
                  </span>
                  <span>
                    <span className="block font-medium">{name}</span>
                    <span className="block text-sm text-slate-500">{blurb}</span>
                  </span>
                </a>
              </li>
            ))}
          </ul>
          <a href="/destinations">View all destinations</a>
        </Dropdown>
        <a href="/experience">Experience</a>
        <button aria-label="Open menu"><MenuIcon className="size-5" /></button>
      </nav>

      <section className="mt-16">
        <p className="inline-flex items-center gap-2 rounded-full border border-sky-200 px-3 py-1 text-xs font-medium uppercase tracking-widest text-sky-700">
          <span className="size-2 rounded-full bg-sky-500" />
          Polar expeditions
        </p>
        <h1 className="text-6xl font-semibold">Discover Untamed Wilderness</h1>
        <p className="max-w-xl text-lg text-slate-600">
          Small-ship voyages to the planet's most remote frontiers, guided by experts.
        </p>
        <div className="mt-8 flex gap-3">
          <a href="/book" className="rounded-full bg-slate-900 px-6 py-3 text-white">Begin your journey</a>
          <a href="/voyages" className="rounded-full border px-6 py-3">Explore voyages</a>
        </div>
      </section>
    </header>
  );
}
