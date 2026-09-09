"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface FinalBlueprintProps {
  content?: string;
}

export default function FinalBlueprint({
  content,
}: FinalBlueprintProps) {
  if (!content) {
    return null;
  }

  return (
    <div className="rounded-xl border bg-white shadow-sm">
      {/* Header */}
      <div className="border-b px-7 py-6">
        <p className="text-xs font-semibold uppercase tracking-[0.12em] text-violet-600">
          Final Architecture
        </p>

        <h2 className="mt-2 text-xl font-semibold tracking-tight text-slate-900">
          Final Blueprint
        </h2>

        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
          The final implementation-oriented architecture blueprint generated
          by Archon.
        </p>
      </div>

      {/* Blueprint content */}
      <article className="px-7 py-8 text-[15px] leading-7 text-slate-700">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ children }) => (
              <h1 className="mb-6 text-2xl font-bold tracking-tight text-slate-950">
                {children}
              </h1>
            ),

            h2: ({ children }) => (
              <div className="mt-12 border-t border-slate-200 pt-7 first:mt-0 first:border-t-0 first:pt-0">
                <h2 className="text-xl font-semibold tracking-tight text-slate-950">
                  {children}
                </h2>
              </div>
            ),

            h3: ({ children }) => (
              <h3 className="mb-3 mt-8 text-base font-semibold text-slate-900">
                {children}
              </h3>
            ),

            h4: ({ children }) => (
              <h4 className="mb-2 mt-6 text-sm font-semibold uppercase tracking-wide text-slate-700">
                {children}
              </h4>
            ),

            p: ({ children }) => (
              <p className="my-4 max-w-4xl leading-7 text-slate-700">
                {children}
              </p>
            ),

            strong: ({ children }) => (
              <strong className="font-semibold text-slate-900">
                {children}
              </strong>
            ),

            ul: ({ children }) => (
              <ul className="my-4 ml-6 list-disc space-y-2 text-slate-700">
                {children}
              </ul>
            ),

            ol: ({ children }) => (
              <ol className="my-4 ml-6 list-decimal space-y-2 text-slate-700">
                {children}
              </ol>
            ),

            li: ({ children }) => (
              <li className="pl-1 leading-7">{children}</li>
            ),

            table: ({ children }) => (
              <div className="my-7 overflow-x-auto rounded-lg border border-slate-200">
                <table className="w-full min-w-[720px] border-collapse text-sm">
                  {children}
                </table>
              </div>
            ),

            thead: ({ children }) => (
              <thead className="bg-slate-50 text-left">
                {children}
              </thead>
            ),

            th: ({ children }) => (
              <th className="border-b border-slate-200 px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">
                {children}
              </th>
            ),

            td: ({ children }) => (
              <td className="border-b border-slate-100 px-4 py-3 align-top leading-6 text-slate-700">
                {children}
              </td>
            ),

            code: ({ children }) => (
              <code className="rounded-md bg-slate-100 px-1.5 py-0.5 font-mono text-[13px] text-slate-800">
                {children}
              </code>
            ),

            pre: ({ children }) => (
              <pre className="my-6 overflow-x-auto rounded-lg border border-slate-200 bg-slate-50 p-4 font-mono text-[13px] leading-6 text-slate-800">
                {children}
              </pre>
            ),

            blockquote: ({ children }) => (
              <blockquote className="my-6 border-l-4 border-violet-200 bg-violet-50/50 px-5 py-3 text-slate-700">
                {children}
              </blockquote>
            ),

            hr: () => (
              <hr className="my-8 border-slate-200" />
            ),
          }}
        >
          {content}
        </ReactMarkdown>
      </article>
    </div>
  );
}