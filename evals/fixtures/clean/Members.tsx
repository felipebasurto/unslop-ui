import { Button } from "./ui";

type Member = { id: string; name: string; role: string; isOwner: boolean; lastSeen: string | null };

export function Members({ members, loading, onInvite }: { members: Member[]; loading: boolean; onInvite: () => void }) {
  if (loading) {
    return <div className="h-8 w-full animate-pulse rounded bg-muted" />;
  }
  return (
    <main className="grid gap-6 p-8">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Members</h1>
        <Button onClick={onInvite}>Invite</Button>
      </header>
      {members.length === 0 ? (
        <p>No members. Invite someone to share this workspace.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th className="text-xs uppercase tracking-wide">Name</th>
              <th className="text-xs uppercase tracking-wide">Role</th>
              <th className="text-xs uppercase tracking-wide">Last seen</th>
            </tr>
          </thead>
          <tbody>
            {members.map((member) => (
              <tr key={member.id}>
                <td>{member.name}</td>
                <td>
                  {member.role}
                  {member.isOwner && <span className="ml-2 rounded bg-muted px-1.5 text-xs">Owner</span>}
                </td>
                <td>{member.lastSeen ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}
