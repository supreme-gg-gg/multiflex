interface GalleryImage {
  url: string;
  caption: string;
}

interface GalleryProps {
  title: string;
  images: GalleryImage[];
}

export default function Gallery({ title, images }: GalleryProps) {
  return (
    <div className="response-card">
      <div className="flex items-start space-x-3 mb-6">
        <div className="w-1 h-12 bg-green-500 rounded-full flex-shrink-0"></div>
        <div className="flex-1 min-w-0">
          <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {images.map((image, index) => (
          <div key={index} className="group">
            <div className="overflow-hidden rounded-lg mb-2">
              <img
                src={image.url}
                alt={image.caption}
                className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
              />
            </div>
            <p className="text-sm text-gray-600 text-center">{image.caption}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
