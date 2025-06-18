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
    <div className="response-card">
      <div className="flex items-start space-x-3">
        <div className="w-1 h-12 bg-yellow-500 rounded-full flex-shrink-0"></div>
        <div className="flex-1 min-w-0">
          <div className="mb-4">
            <div className="text-2xl text-gray-300 mb-2">"</div>
            <p className="text-gray-700 italic leading-relaxed">{quote}</p>
            <div className="text-2xl text-gray-300 text-right">"</div>
          </div>

          <div className="flex items-center space-x-3">
            {avatar ? (
              <img
                src={avatar}
                alt={author}
                className="w-10 h-10 rounded-full object-cover"
              />
            ) : (
              <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium text-sm">
                {author.charAt(0)}
              </div>
            )}
            <div className="min-w-0">
              <div className="font-medium text-gray-900">{author}</div>
              <div className="text-sm text-gray-600">{role}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
