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
  return (
    <div className="card p-0 overflow-hidden">
      <div className="relative h-64 md:h-80">
        <img src={image} alt={title} className="w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
        <div className="absolute bottom-6 left-6 right-6 text-white">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">{title}</h1>
          <p className="text-lg text-white/90 mb-4">{subtitle}</p>
          {buttonText && (
            <button
              onClick={() => buttonLink && window.open(buttonLink, "_blank")}
              className="btn-primary text-white py-3 px-6 rounded-xl font-medium animate-pulse-hover"
            >
              {buttonText}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
