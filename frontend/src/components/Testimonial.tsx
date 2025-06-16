interface TestimonialProps {
  quote: string;
  author: string;
  role: string;
  avatar?: string;
}

export default function Testimonial({
  quote,
  author,
  role,
  avatar,
}: TestimonialProps) {
  return (
    <div className="card p-6">
      <div className="flex items-start space-x-3">
        <div className="w-2 h-16 bg-gradient-to-b from-yellow-400 to-orange-500 rounded-full"></div>
        <div className="flex-1">
          <div className="mb-6">
            <div className="text-4xl text-gray-300 mb-2">"</div>
            <p className="text-lg text-gray-700 italic leading-relaxed">
              {quote}
            </p>
            <div className="text-4xl text-gray-300 text-right">"</div>
          </div>

          <div className="flex items-center space-x-4">
            {avatar ? (
              <img
                src={avatar}
                alt={author}
                className="w-12 h-12 rounded-full object-cover"
              />
            ) : (
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-blue-500 flex items-center justify-center text-white font-bold">
                {author.charAt(0)}
              </div>
            )}
            <div>
              <div className="font-semibold text-gray-800">{author}</div>
              <div className="text-sm text-gray-600">{role}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
