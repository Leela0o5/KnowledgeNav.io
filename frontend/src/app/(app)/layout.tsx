import { redirect } from "next/navigation";
import { getSession } from "@/lib/auth";
import { SessionList } from "@/components/sidebar/SessionList";
import { SidebarFooter } from "@/components/sidebar/SidebarFooter";

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getSession();
  if (!user) {
    redirect("/");
  }

  return (
    <div className="flex h-screen bg-background">
      <aside className="w-64 border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <span className="font-semibold text-foreground">KnowledgeNav</span>
        </div>
        <div className="flex-1 overflow-y-auto">
          <SessionList />
        </div>
        <SidebarFooter email={user.email} />
      </aside>
      <main className="flex-1 overflow-hidden">{children}</main>
    </div>
  );
}
