import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import rehypeRaw from 'rehype-raw'

interface MarkdownRendererProps {
  content: string
  className?: string
}

export function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  return (
    <div className={`agricultural-prose ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight, rehypeRaw]}
        components={{
          // Executive Summary styling
          h1: ({ children }) => (
            <div className="agricultural-heading-1">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-green-600 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-bold">🌾</span>
                </div>
                <h1 className="text-2xl font-bold text-green-700 m-0">
                  {children}
                </h1>
              </div>
              <div className="w-full h-1 bg-gradient-to-r from-green-400 via-green-500 to-green-600 rounded-full mb-6"></div>
            </div>
          ),
          
          // Section headers with agricultural theme
          h2: ({ children }) => (
            <div className="agricultural-heading-2 mt-8 mb-4">
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">✨</span>
                </div>
                <h2 className="text-xl font-bold text-emerald-700 m-0">
                  {children}
                </h2>
              </div>
              <div className="w-20 h-0.5 bg-emerald-400 rounded-full mt-2"></div>
            </div>
          ),
          
          // Subsection headers
          h3: ({ children }) => (
            <div className="agricultural-heading-3 mt-6 mb-3">
              <h3 className="text-lg font-semibold text-green-600 m-0 flex items-center gap-2">
                <span className="w-2 h-6 bg-green-500 rounded-full"></span>
                {children}
              </h3>
            </div>
          ),
          
          h4: ({ children }) => (
            <h4 className="text-base font-semibold text-green-600 mb-2 mt-4 flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
              {children}
            </h4>
          ),
          
          // Enhanced paragraph styling
          p: ({ children }) => (
            <p className="text-gray-700 mb-4 leading-relaxed text-base">
              {children}
            </p>
          ),
          
          // Beautiful list styling
          ul: ({ children }) => (
            <ul className="agricultural-list space-y-3 mb-6 ml-4">
              {children}
            </ul>
          ),
          
          ol: ({ children }) => (
            <ol className="agricultural-ordered-list space-y-3 mb-6 ml-6">
              {children}
            </ol>
          ),
          
          li: ({ children }) => (
            <li className="agricultural-list-item">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2.5 flex-shrink-0"></div>
                <span className="text-gray-700 leading-relaxed">{children}</span>
              </div>
            </li>
          ),
          
          // Enhanced text styling
          strong: ({ children }) => (
            <strong className="font-semibold text-green-700 bg-green-50 px-1 py-0.5 rounded">
              {children}
            </strong>
          ),
          
          em: ({ children }) => (
            <em className="italic text-emerald-600 font-medium">
              {children}
            </em>
          ),
          
          // Beautiful blockquotes
          blockquote: ({ children }) => (
            <blockquote className="agricultural-blockquote">
              <div className="relative bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-500 rounded-r-lg p-4 my-6">
                <div className="absolute top-2 left-2">
                  <span className="text-green-500 text-2xl font-bold">"</span>
                </div>
                <div className="ml-4">
                  {children}
                </div>
              </div>
            </blockquote>
          ),
          
          // Code styling
          code: ({ children, className }) => {
            const isInline = !className
            if (isInline) {
              return (
                <code className="bg-gray-100 text-green-700 px-2 py-1 rounded text-sm font-mono border">
                  {children}
                </code>
              )
            }
            return (
              <code className={className}>
                {children}
              </code>
            )
          },
          
          pre: ({ children }) => (
            <pre className="bg-gray-50 border border-gray-200 rounded-lg p-4 overflow-x-auto mb-6 text-sm shadow-sm">
              {children}
            </pre>
          ),
          
          // Enhanced table styling
          table: ({ children }) => (
            <div className="overflow-x-auto mb-6 rounded-lg border border-gray-200 shadow-sm">
              <table className="min-w-full agricultural-table">
                {children}
              </table>
            </div>
          ),
          
          thead: ({ children }) => (
            <thead className="bg-gradient-to-r from-green-500 to-emerald-500 text-white">
              {children}
            </thead>
          ),
          
          th: ({ children }) => (
            <th className="px-6 py-3 text-left text-sm font-semibold">
              {children}
            </th>
          ),
          
          td: ({ children }) => (
            <td className="px-6 py-4 text-sm text-gray-700 border-b border-gray-100">
              {children}
            </td>
          ),
          
          // Enhanced links
          a: ({ children, href }) => (
            <a 
              href={href} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-green-600 hover:text-green-700 underline decoration-green-300 hover:decoration-green-500 transition-colors font-medium"
            >
              {children}
            </a>
          ),
          
          // Image styling
          img: ({ src, alt }) => (
            <img 
              src={src} 
              alt={alt} 
              className="max-w-full h-auto rounded-lg border border-gray-200 my-6 shadow-sm"
            />
          )
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

// Streaming text component for live typing effect
interface StreamingTextProps {
  text: string
  speed?: number
  className?: string
}

export function StreamingText({ text, speed = 30, className = '' }: StreamingTextProps) {
  return (
    <div className={`agricultural-streaming ${className}`}>
      <MarkdownRenderer content={text} />
      <span className="inline-block w-0.5 h-5 bg-green-500 animate-pulse ml-1 align-text-bottom"></span>
    </div>
  )
}
