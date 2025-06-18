interface HeroProps {
  title: string;
  subtitle: string;
  image: string;
  buttonText?: string;
  buttonLink?: string;
}

export default function Hero({
  title,
  subtitle,
  image,
  buttonText,
  buttonLink,
}: HeroProps) {
  const handleButtonClick = (e: React.MouseEvent) => {
    e.preventDefault();
    if (buttonLink && buttonLink.startsWith("http")) {
      window.open(buttonLink, "_blank", "noopener,noreferrer");
    }
  };

  return (
    <div className="response-card p-0 overflow-hidden">
      <div className="relative h-64 md:h-80">
        <img src={image} alt={title} className="w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
        <div className="absolute bottom-6 left-6 right-6 text-white">
          <h1 className="text-2xl md:text-3xl font-bold mb-2">{title}</h1>
          <p className="text-base text-white/90 mb-4">{subtitle}</p>
          {buttonText && buttonLink && (
            <button
              onClick={handleButtonClick}
              className="bg-white text-gray-900 py-2 px-4 rounded-lg font-medium hover:bg-gray-100 transition-colors"
            >
              {buttonText}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
