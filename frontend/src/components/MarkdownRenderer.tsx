'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import 'highlight.js/styles/github-dark.css'

interface MarkdownRendererProps {
  content: string
  className?: string
}

export function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  // Fallback for empty content
  if (!content || content.trim() === '') {
    return (
      <div className={`bot-message ${className}`} style={{ color: '#ff0000', fontWeight: 'bold' }}>
        <p>ERROR: No content received from backend</p>
      </div>
    )
  }

  return (
    <div className={`prose prose-green max-w-none bot-message ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
          h1: ({ children }) => (
            <h1 className="text-2xl font-bold mb-4 flex items-center" style={{ color: '#166534 !important' }}>
              🌾 {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-xl font-semibold mb-3 flex items-center" style={{ color: '#15803d !important' }}>
              🌱 {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-lg font-medium mb-2 flex items-center" style={{ color: '#16a34a !important' }}>
              🌿 {children}
            </h3>
          ),
          p: ({ children }) => (
            <p className="mb-4 leading-relaxed" style={{ color: '#374151 !important' }}>
              {children}
            </p>
          ),
          ul: ({ children }) => (
            <ul className="list-none space-y-2 mb-4" style={{ color: '#374151 !important' }}>
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-inside space-y-2 mb-4" style={{ color: '#374151 !important' }}>
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="flex items-start space-x-2" style={{ color: '#374151 !important' }}>
              <span className="mt-1" style={{ color: '#16a34a !important' }}>•</span>
              <span style={{ color: '#374151 !important' }}>{children}</span>
            </li>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-green-500 pl-4 py-2 bg-green-50 rounded-r mb-4" style={{ color: '#374151 !important' }}>
              {children}
            </blockquote>
          ),
          code: ({ children, className }) => {
            const isInline = !className
            if (isInline) {
              return (
                <code className="bg-green-100 px-1 py-0.5 rounded text-sm" style={{ color: '#166534 !important' }}>
                  {children}
                </code>
              )
            }
            return (
              <code className={className} style={{ color: '#374151 !important' }}>
                {children}
              </code>
            )
          },
          pre: ({ children }) => (
            <pre className="bg-gray-900 p-4 rounded-lg overflow-x-auto mb-4" style={{ color: '#16a34a !important' }}>
              {children}
            </pre>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto mb-4">
              <table className="min-w-full border border-green-300">
                {children}
              </table>
            </div>
          ),
          th: ({ children }) => (
            <th className="border border-green-300 bg-green-100 px-4 py-2 text-left font-semibold" style={{ color: '#166534 !important' }}>
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="border border-green-300 px-4 py-2" style={{ color: '#374151 !important' }}>
              {children}
            </td>
          ),
          strong: ({ children }) => (
            <strong className="font-bold" style={{ color: '#166534 !important' }}>
              {children}
            </strong>
          ),
          em: ({ children }) => (
            <em className="italic" style={{ color: '#15803d !important' }}>
              {children}
            </em>
          ),
          a: ({ children, href }) => (
            <a href={href} className="underline hover:no-underline" style={{ color: '#16a34a !important' }}>
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
