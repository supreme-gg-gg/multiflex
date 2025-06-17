interface CodeBlockItem {
    code: string;
    label: string;
    language?: string;
}
  
interface CodeBlocksProps {
    title: string;
    blocks: CodeBlockItem[];
}
  
export default function CodeBlocks({ title, blocks }: CodeBlocksProps) {
    return (
      <div className="card p-6">
        <div className="flex items-start space-x-3 mb-6">
          <div className="w-2 h-16 bg-gradient-to-b from-purple-400 to-indigo-500 rounded-full"></div>
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-800">{title}</h2>
          </div>
        </div>
  
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {blocks.map((block, index) => (
            <div
              key={index}
              className="p-4 rounded-lg bg-gradient-to-br from-gray-50 to-gray-100 hover:from-gray-100 hover:to-gray-200 transition-all"
            >
              <div className="text-sm font-medium text-gray-600 mb-2">
                {block.label}
                {block.language && (
                  <span className="ml-2 text-xs text-gray-500">
                    ({block.language})
                  </span>
                )}
              </div>
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-md text-sm overflow-x-auto">
                <code className={`language-${block.language || "plaintext"}`}>
                  {block.code}
                </code>
              </pre>
            </div>
          ))}
        </div>
      </div>
    );
}
  