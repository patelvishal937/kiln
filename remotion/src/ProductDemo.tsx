import { AbsoluteFill, Series } from "remotion";
import { FeatureScene } from "./scenes/FeatureScene";
import { Intro } from "./scenes/Intro";
import { Outro } from "./scenes/Outro";
import { INTRO, LaunchProps, OUTRO, SCENE } from "./types";
import { useGoogleFont } from "./useGoogleFont";

// Hook → one scene per benefit (real screenshots) → CTA. Same component renders 16:9 and 9:16.
export const ProductDemo: React.FC<LaunchProps> = (p) => {
  useGoogleFont(p.headingFont);
  useGoogleFont("Inter");

  return (
    <AbsoluteFill style={{ background: p.colors.background }}>
      <Series>
        <Series.Sequence durationInFrames={INTRO}>
          <Intro p={p} />
        </Series.Sequence>
        {p.scenes.map((scene, i) => (
          <Series.Sequence key={i} durationInFrames={SCENE}>
            <FeatureScene p={p} scene={scene} index={i} />
          </Series.Sequence>
        ))}
        <Series.Sequence durationInFrames={OUTRO}>
          <Outro p={p} />
        </Series.Sequence>
      </Series>
    </AbsoluteFill>
  );
};
