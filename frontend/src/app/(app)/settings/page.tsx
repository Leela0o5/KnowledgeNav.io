import { getSession } from "@/lib/auth";

export default async function SettingsPage() {
  const user = await getSession();

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Settings</h1>
      {user && (
        <div className="border border-gray-200 rounded-md p-4 space-y-2">
          <div className="text-sm">
            <span className="font-medium">Name:</span> {user.name}
          </div>
          <div className="text-sm">
            <span className="font-medium">Email:</span> {user.email}
          </div>
          <div className="text-sm">
            <span className="font-medium">Role:</span> {user.role}
          </div>
        </div>
      )}
    </div>
  );
}
