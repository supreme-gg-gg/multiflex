interface CardProps {
  title: string;
  content: string;
  image?: string;
  badge?: string;
}

export default function Card({ title, content, image, badge }: CardProps) {
  return (
    <div className="response-card">
      {image && (
        <div className="mb-4 overflow-hidden rounded-lg">
          <img
            src={image}
            alt={title}
            className="w-full h-48 object-cover hover:scale-105 transition-transform duration-300"
          />
        </div>
      )}
      <div className="flex items-start space-x-3">
        <div className="w-1 h-12 bg-blue-500 rounded-full flex-shrink-0"></div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-3">
            <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
            {badge && (
              <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
                {badge}
              </span>
            )}
          </div>
          <p className="text-gray-600 leading-relaxed">{content}</p>
        </div>
      </div>
    </div>
  );
}
