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
    <div className="response-card">
      <div className="flex items-start space-x-3 mb-6">
        <div className="w-1 h-12 bg-orange-500 rounded-full flex-shrink-0"></div>
        <div className="flex-1 min-w-0">
          <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
        </div>
      </div>

      <ul className="space-y-3">
        {items.map((item, index) => (
          <li
            key={index}
            className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
          >
            {item.icon && (
              <span className="text-xl flex-shrink-0">{item.icon}</span>
            )}
            <span className="text-gray-700">{item.text}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
