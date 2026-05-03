import { ChatWindow } from "@/components/chat/ChatWindow";

interface Props {
  params: { sessionId: string };
}

export default function SessionPage({ params }: Props) {
  return <ChatWindow sessionId={params.sessionId} />;
}
