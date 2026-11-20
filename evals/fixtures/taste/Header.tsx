export function Header({ user, deploy }) {
  return (
    <header>
      <h1>🚀 Rocket Deploy</h1>
      <span className="rounded bg-sky-100 px-2 text-xs">Beta</span>
      <p>Welcome back, {user.name}!</p>
      <p>Deploy {deploy.id} is ready!</p>
    </header>
  );
}
