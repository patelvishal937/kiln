import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { LaunchProps } from "./types";

// Seamless, text-free background loop in brand colours. Every motion is a whole number of
// sine periods over the composition, so the last frame flows into the first.
export const HeroLoop: React.FC<LaunchProps> = (p) => {
  const frame = useCurrentFrame();
  const { durationInFrames, width, height } = useVideoConfig();
  const t = (frame / durationInFrames) * Math.PI * 2;

  const blobs = [
    { c: p.colors.primary, r: 0.55, x: 0.25, y: 0.35, ax: 0.08, ay: 0.06, k: 1 },
    { c: p.colors.accent, r: 0.35, x: 0.72, y: 0.62, ax: 0.07, ay: 0.08, k: 2 },
    { c: p.colors.secondary, r: 0.6, x: 0.6, y: 0.2, ax: 0.05, ay: 0.05, k: 1 },
    { c: p.colors.primary, r: 0.4, x: 0.15, y: 0.85, ax: 0.06, ay: 0.04, k: 3 },
  ];
  const size = Math.max(width, height);

  return (
    <AbsoluteFill style={{ background: p.colors.secondary, overflow: "hidden" }}>
      {blobs.map((b, i) => {
        const cx = (b.x + Math.sin(t * b.k + i) * b.ax) * width;
        const cy = (b.y + Math.cos(t * b.k + i * 1.7) * b.ay) * height;
        const d = b.r * size;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: cx - d / 2,
              top: cy - d / 2,
              width: d,
              height: d,
              borderRadius: "50%",
              background: `radial-gradient(circle, ${b.c} 0%, ${b.c}00 70%)`,
              filter: "blur(60px)",
              opacity: 0.85,
              mixBlendMode: "screen",
            }}
          />
        );
      })}
      {/* subtle grid for depth */}
      <AbsoluteFill
        style={{
          backgroundImage: "linear-gradient(#ffffff0d 1px, transparent 1px), linear-gradient(90deg, #ffffff0d 1px, transparent 1px)",
          backgroundSize: "80px 80px",
          backgroundPosition: `${Math.sin(t) * 20}px ${Math.cos(t) * 20}px`,
        }}
      />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, #00000040 0%, #00000000 40%, #00000055 100%)" }} />
    </AbsoluteFill>
  );
};
