/* eslint-disable @typescript-eslint/no-explicit-any */
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { cn } from '../../lib/utils';

const Markdown = ReactMarkdown as any;

interface Props {
  content: string;
  className?: string;
}

const components: Record<string, (props: any) => JSX.Element | null> = {
  h1: ({ children }) => (
    <h1 className="text-xl font-bold text-slate-800 mt-5 mb-2 pb-2 border-b border-slate-100">
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-base font-bold text-slate-800 mt-4 mb-2">{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-sm font-semibold text-slate-700 mt-3 mb-1">{children}</h3>
  ),
  p: ({ children }) => (
    <p className="text-sm text-slate-700 leading-7 mb-3 last:mb-0">{children}</p>
  ),
  ul: ({ children }) => <ul className="mb-3 space-y-1.5 pl-0">{children}</ul>,
  ol: ({ children }) => (
    <ol className="mb-3 space-y-1.5 list-decimal pl-5">{children}</ol>
  ),
  li: ({ children }) => (
    <li className="text-sm text-slate-700 leading-7">{children}</li>
  ),
  strong: ({ children }) => (
    <strong className="font-semibold text-slate-800">{children}</strong>
  ),
  em: ({ children }) => <em className="italic text-slate-600">{children}</em>,
  blockquote: ({ children }) => (
    <blockquote className="my-3 pl-4 border-l-[3px] border-blue-300 bg-blue-50/50 py-2 pr-3 rounded-r-lg">
      <div className="text-sm text-slate-600 italic">{children}</div>
    </blockquote>
  ),
  hr: () => <hr className="my-4 border-slate-100" />,
  pre: ({ children }) => (
    <pre className="my-3 bg-slate-900 rounded-xl overflow-x-auto">{children}</pre>
  ),
  code: ({ children, className: cls }) => {
    if (cls) {
      return (
        <code className="block p-4 text-xs font-mono text-slate-200 leading-6 whitespace-pre">
          {children}
        </code>
      );
    }
    return (
      <code className="bg-blue-50 text-blue-600 rounded-md px-1.5 py-0.5 text-[12px] font-mono font-medium">
        {children}
      </code>
    );
  },
  table: ({ children }) => (
    <div className="my-3 overflow-x-auto rounded-xl border border-slate-200">
      <table className="w-full text-sm border-collapse">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-slate-50">{children}</thead>,
  th: ({ children }) => (
    <th className="px-4 py-2.5 text-left text-xs font-bold text-slate-600 uppercase tracking-wide border-b border-slate-200">
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td className="px-4 py-2.5 text-sm text-slate-600 border-b border-slate-100">
      {children}
    </td>
  ),
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-blue-600 font-medium underline underline-offset-2 hover:text-blue-800 transition-colors"
    >
      {children}
    </a>
  ),
};

export default function MarkdownContent({ content, className }: Props) {
  return (
    <div className={cn('markdown-body', className)}>
      <Markdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]} components={components}>
        {content}
      </Markdown>
    </div>
  );
}
