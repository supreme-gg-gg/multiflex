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
    <div className="card p-6">
      <div className="flex items-start space-x-3 mb-6">
        <div className="w-2 h-16 bg-gradient-to-b from-green-400 to-blue-500 rounded-full"></div>
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-gray-800">{title}</h2>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {images.map((image, index) => (
          <div key={index} className="group">
            <div className="overflow-hidden rounded-lg mb-2">
              <img
                src={image.url}
                alt={image.caption}
                className="w-full h-48 object-cover group-hover:scale-110 transition-transform duration-300"
              />
            </div>
            <p className="text-sm text-gray-600 text-center">{image.caption}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
