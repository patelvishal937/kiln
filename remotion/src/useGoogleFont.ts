import { useEffect, useState } from "react";
import { continueRender, delayRender } from "remotion";

// Loads a Google Font by family name and holds the render until it is ready
// (falls back to the system stack after 8s so a font outage never blocks a render).
export const useGoogleFont = (family: string) => {
  const [handle] = useState(() => delayRender(`font: ${family}`));

  useEffect(() => {
    const done = () => continueRender(handle);
    const timer = setTimeout(done, 8000);
    const id = `gf-${family.replace(/\s+/g, "-")}`;
    const loadFace = () =>
      document.fonts
        .load(`700 48px "${family}"`)
        .catch(() => undefined)
        .finally(() => {
          clearTimeout(timer);
          done();
        });

    if (document.getElementById(id)) {
      loadFace();
      return () => clearTimeout(timer);
    }
    const link = document.createElement("link");
    link.id = id;
    link.rel = "stylesheet";
    link.href = `https://fonts.googleapis.com/css2?family=${encodeURIComponent(family).replace(/%20/g, "+")}:wght@400;600;700&display=block`;
    link.onload = loadFace;
    link.onerror = () => {
      clearTimeout(timer);
      done();
    };
    document.head.appendChild(link);
    return () => clearTimeout(timer);
  }, [family, handle]);
};

export const fontStack = (family: string) => `"${family}", "Inter", system-ui, -apple-system, sans-serif`;
