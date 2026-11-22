type NavItem = { id: string; label: string; href: string; count?: number };

export function Sidebar({ items, activeId, settingsCount }: { items: NavItem[]; activeId: string; settingsCount: number }) {
  return (
    <nav className="flex w-60 flex-col gap-1 border-r p-2">
      {items.map((item) => (
        <a
          key={item.id}
          href={item.href}
          aria-current={item.id === activeId ? "page" : undefined}
          className={
            "flex items-center gap-2 rounded-md px-3 py-1.5 text-sm " +
            (item.id === activeId ? "bg-muted font-medium" : "text-muted-foreground")
          }
        >
          <span>{item.label}</span>
          {item.count != null && <span className="ml-auto text-xs">{item.count}</span>}
        </a>
      ))}
      <a
        href="/settings"
        className="flex items-center gap-2 rounded-md py-1.5 pl-4 pr-3 text-sm text-muted-foreground"
      >
        <span>Settings</span>
        <span className="ml-auto mr-1 text-xs">{settingsCount}</span>
      </a>
    </nav>
  );
}
