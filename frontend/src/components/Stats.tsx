interface StatItem {
  value: string;
  label: string;
  icon?: string;
}

interface StatsProps {
  title: string;
  data: StatItem[];
}

export default function Stats({ title, data }: StatsProps) {
  return (
    <div className="response-card">
      <div className="flex items-start space-x-3 mb-6">
        <div className="w-1 h-12 bg-cyan-500 rounded-full flex-shrink-0"></div>
        <div className="flex-1 min-w-0">
          <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {data.map((stat, index) => (
          <div
            key={index}
            className="text-center p-4 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
          >
            {stat.icon && <div className="text-2xl mb-2">{stat.icon}</div>}
            <div className="text-2xl font-bold text-gray-900 mb-1">
              {stat.value}
            </div>
            <div className="text-sm text-gray-600">{stat.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
