import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { LaunchProps } from "../types";
import { fontStack } from "../useGoogleFont";

export const Intro: React.FC<{ p: LaunchProps }> = ({ p }) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();
  const vertical = height > width;
  const pop = spring({ frame, fps, config: { damping: 14 } });
  const brandIn = spring({ frame: frame - 28, fps, config: { damping: 18 } });
  const out = interpolate(frame, [durationInFrames - 12, durationInFrames], [1, 0], { extrapolateLeft: "clamp" });

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(120% 120% at 20% 10%, ${p.colors.primary} 0%, ${p.colors.secondary} 70%)`,
        justifyContent: "center",
        alignItems: "center",
        padding: vertical ? 80 : 160,
        opacity: out,
      }}
    >
      <div
        style={{
          fontFamily: fontStack(p.headingFont),
          fontWeight: 700,
          color: "#fff",
          fontSize: vertical ? 92 : 104,
          lineHeight: 1.05,
          textAlign: "center",
          letterSpacing: -2,
          transform: `scale(${0.85 + pop * 0.15})`,
          opacity: pop,
        }}
      >
        {p.hook}
      </div>
      <div
        style={{
          marginTop: 48,
          display: "flex",
          alignItems: "center",
          gap: 18,
          opacity: brandIn,
          transform: `translateY(${(1 - brandIn) * 30}px)`,
        }}
      >
        <div style={{ width: 22, height: 22, borderRadius: 6, background: p.colors.accent }} />
        <span style={{ fontFamily: fontStack(p.headingFont), color: "#fff", fontSize: vertical ? 48 : 44, fontWeight: 600 }}>
          {p.brandName}
        </span>
      </div>
    </AbsoluteFill>
  );
};
