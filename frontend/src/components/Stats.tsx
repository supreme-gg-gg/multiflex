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
    <div className="card p-6">
      <div className="flex items-start space-x-3 mb-6">
        <div className="w-2 h-16 bg-gradient-to-b from-cyan-400 to-blue-500 rounded-full"></div>
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-gray-800">{title}</h2>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {data.map((stat, index) => (
          <div
            key={index}
            className="text-center p-4 rounded-lg bg-gradient-to-br from-gray-50 to-gray-100 hover:from-gray-100 hover:to-gray-200 transition-all"
          >
            {stat.icon && <div className="text-3xl mb-2">{stat.icon}</div>}
            <div className="text-3xl font-bold text-gray-800 mb-1">
              {stat.value}
            </div>
            <div className="text-sm text-gray-600">{stat.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
