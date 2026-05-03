interface Props {
  content: string;
}

export function StreamingMessage({ content }: Props) {
  if (!content) {
    return (
      <div className="flex justify-start mb-4">
        <div className="bg-gray-100 rounded-lg px-4 py-2">
          <div className="flex space-x-1">
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-2xl bg-gray-100 text-gray-900 px-4 py-2 rounded-lg text-sm">
        {content}
        <span className="inline-block w-0.5 h-4 bg-gray-500 ml-0.5 animate-pulse" />
      </div>
    </div>
  );
}
