import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { LaunchProps } from "../types";
import { fontStack } from "../useGoogleFont";

export const Outro: React.FC<{ p: LaunchProps }> = ({ p }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const vertical = height > width;
  const inn = spring({ frame, fps, config: { damping: 15 } });
  const btn = spring({ frame: frame - 14, fps, config: { damping: 12 } });
  const fadeIn = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(120% 120% at 80% 90%, ${p.colors.primary} 0%, ${p.colors.secondary} 70%)`,
        justifyContent: "center",
        alignItems: "center",
        padding: vertical ? 80 : 160,
        opacity: fadeIn,
      }}
    >
      <div
        style={{
          fontFamily: fontStack(p.headingFont),
          color: "#fff",
          fontWeight: 700,
          fontSize: vertical ? 110 : 120,
          letterSpacing: -3,
          transform: `scale(${0.9 + inn * 0.1})`,
          opacity: inn,
        }}
      >
        {p.brandName}
      </div>
      <div style={{ fontFamily: fontStack("Inter"), color: "#ffffffcc", fontSize: vertical ? 44 : 42, marginTop: 20, opacity: inn, textAlign: "center" }}>
        {p.tagline}
      </div>
      <div
        style={{
          marginTop: 60,
          padding: vertical ? "30px 56px" : "26px 52px",
          borderRadius: 999,
          background: p.colors.accent,
          color: p.colors.secondary,
          fontFamily: fontStack(p.headingFont),
          fontWeight: 700,
          fontSize: vertical ? 44 : 38,
          transform: `scale(${btn})`,
        }}
      >
        {p.cta}
      </div>
    </AbsoluteFill>
  );
};
