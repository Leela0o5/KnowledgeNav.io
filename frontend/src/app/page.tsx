import { getLoginUrl } from "@/lib/auth";

export default function LandingPage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-background">
      <div className="max-w-md w-full space-y-8 px-4">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-foreground">KnowledgeNav</h1>
          <p className="mt-2 text-gray-500">Ask questions across your document corpus</p>
        </div>
        <div className="space-y-3">
          <a
            href={getLoginUrl("google")}
            className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Continue with Google
          </a>
          <a
            href={getLoginUrl("github")}
            className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Continue with GitHub
          </a>
        </div>
      </div>
    </main>
  );
}
