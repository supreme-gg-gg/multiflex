interface CardProps {
  title: string;
  content: string;
  image?: string;
  badge?: string;
}

export default function Card({ title, content, image, badge }: CardProps) {
  return (
    <div className="card p-6">
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
        <div className="w-2 h-16 bg-gradient-to-b from-purple-400 to-blue-500 rounded-full"></div>
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-3">
            <h2 className="text-2xl font-bold text-gray-800">{title}</h2>
            {badge && (
              <span className="px-3 py-1 bg-gradient-to-r from-purple-400 to-blue-500 text-white text-sm rounded-full">
                {badge}
              </span>
            )}
          </div>
          <p className="text-gray-600 leading-relaxed text-lg">{content}</p>
        </div>
      </div>
    </div>
  );
}
