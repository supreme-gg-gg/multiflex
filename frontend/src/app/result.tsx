import { useState, useEffect } from "react";
import { API_ENDPOINTS } from "../lib/api";

interface ComponentProps {
  type: string;
  props: {
    title?: string;
    content?: string;
    [key: string]: any;
  };
}

export default function Result() {
  const [loading, setLoading] = useState(true);
  const [components, setComponents] = useState<ComponentProps[] | null>(null);

  useEffect(() => {
    const prompt = sessionStorage.getItem("prompt");
    if (prompt) {
      fetch(API_ENDPOINTS.agent, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt }),
      })
        .then((res) => res.json())
        .then((data) => {
          setComponents(data.components);
          setLoading(false);
        })
        .catch((err) => {
          console.error(err);
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Loading...</h1>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      {components && components.length > 0 ? (
        components.map((comp, index) => {
          if (comp.type === "card") {
            return (
              <div key={index} className="border p-4 mb-4">
                <h2 className="text-xl font-bold mb-2">{comp.props.title}</h2>
                <p>{comp.props.content}</p>
              </div>
            );
          }
          return (
            <div key={index} className="border p-4 mb-4">
              Unknown component type: {comp.type}
            </div>
          );
        })
      ) : (
        <p>No components returned.</p>
      )}
    </div>
  );
}
