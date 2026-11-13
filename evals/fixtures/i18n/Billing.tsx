import { useTranslation } from "react-i18next";
import { Button } from "./ui";

export function Billing({ onUpgrade }: { onUpgrade: () => void }) {
  const { t } = useTranslation();
  return (
    <main className="grid gap-4 p-8">
      <p className="text-xs uppercase tracking-widest text-violet-500">Account</p>
      <h1 className="text-2xl font-semibold">{t("billing.title")}</h1>
      <p className="text-muted-foreground">{t("billing.subtitle")}</p>
      <Button onClick={onUpgrade}>{t("billing.cta")}</Button>
    </main>
  );
}
