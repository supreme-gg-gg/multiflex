interface ListItem {
  text: string;
  icon?: string;
}

interface ListProps {
  title: string;
  items: ListItem[];
}

export default function List({ title, items }: ListProps) {
  return (
    <div className="card p-6">
      <div className="flex items-start space-x-3 mb-6">
        <div className="w-2 h-16 bg-gradient-to-b from-orange-400 to-pink-500 rounded-full"></div>
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-gray-800">{title}</h2>
        </div>
      </div>

      <ul className="space-y-4">
        {items.map((item, index) => (
          <li
            key={index}
            className="flex items-center space-x-4 p-3 rounded-lg hover:bg-gray-50 transition-colors"
          >
            {item.icon && (
              <span className="text-2xl flex-shrink-0">{item.icon}</span>
            )}
            <span className="text-lg text-gray-700">{item.text}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
