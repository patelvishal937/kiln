import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { LaunchProps, Scene } from "../types";
import { fontStack } from "../useGoogleFont";

// One benefit: caption on one side, the real product screenshot in a device frame on the other,
// with a slow Ken Burns push so static screenshots feel alive.
export const FeatureScene: React.FC<{ p: LaunchProps; scene: Scene; index: number }> = ({ p, scene, index }) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();
  const vertical = height > width;

  const enter = spring({ frame, fps, config: { damping: 16 } });
  const textIn = spring({ frame: frame - 8, fps, config: { damping: 18 } });
  const fade = interpolate(frame, [0, 10, durationInFrames - 10, durationInFrames], [0, 1, 1, 0], {
    extrapolateRight: "clamp",
  });
  const zoom = interpolate(frame, [0, durationInFrames], [1.0, 1.08]);
  const flip = !vertical && index % 2 === 1;

  const frameW = vertical ? width * 0.62 : width * 0.56;
  const frameH = vertical ? frameW * (844 / 390) : frameW * (900 / 1440);

  const device = (
    <div
      style={{
        width: frameW,
        height: frameH + (vertical ? 0 : 40),
        borderRadius: vertical ? 56 : 18,
        overflow: "hidden",
        background: "#fff",
        border: vertical ? `14px solid ${p.colors.secondary}` : "none",
        boxShadow: `0 40px 120px -30px ${p.colors.primary}88, 0 10px 30px rgba(0,0,0,0.18)`,
        transform: `translateY(${(1 - enter) * 80}px)`,
        flexShrink: 0,
      }}
    >
      {!vertical && (
        <div style={{ height: 40, background: "#EEF0F5", display: "flex", alignItems: "center", gap: 8, paddingLeft: 16 }}>
          {["#FF5F57", "#FEBC2E", "#28C840"].map((c) => (
            <div key={c} style={{ width: 12, height: 12, borderRadius: 6, background: c }} />
          ))}
        </div>
      )}
      <div style={{ width: "100%", height: frameH, overflow: "hidden", position: "relative" }}>
        {scene.image ? (
          <Img
            src={staticFile(scene.image)}
            style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "top", transform: `scale(${zoom})`, transformOrigin: "50% 0%" }}
          />
        ) : (
          <AbsoluteFill
            style={{
              background: `linear-gradient(135deg, ${p.colors.primary}22, ${p.colors.accent}33)`,
              justifyContent: "center",
              alignItems: "center",
              fontFamily: fontStack(p.headingFont),
              fontSize: 64,
              color: p.colors.secondary,
              fontWeight: 700,
            }}
          >
            {p.brandName}
          </AbsoluteFill>
        )}
      </div>
    </div>
  );

  const copy = (
    <div style={{ maxWidth: vertical ? width - 140 : width * 0.32, opacity: textIn, transform: `translateY(${(1 - textIn) * 24}px)` }}>
      <div style={{ fontFamily: fontStack(p.headingFont), color: p.colors.accent, fontSize: vertical ? 34 : 26, fontWeight: 700, letterSpacing: 2 }}>
        {String(index + 1).padStart(2, "0")}
      </div>
      <div
        style={{
          fontFamily: fontStack(p.headingFont),
          color: p.colors.text,
          fontSize: vertical ? 76 : 68,
          fontWeight: 700,
          lineHeight: 1.05,
          letterSpacing: -1.5,
          marginTop: 12,
        }}
      >
        {scene.title}
      </div>
      <div style={{ fontFamily: fontStack("Inter"), color: p.colors.text, opacity: 0.75, fontSize: vertical ? 40 : 34, lineHeight: 1.35, marginTop: 20 }}>
        {scene.caption}
      </div>
    </div>
  );

  return (
    <AbsoluteFill
      style={{
        background: p.colors.background,
        opacity: fade,
        flexDirection: vertical ? "column" : flip ? "row-reverse" : "row",
        justifyContent: "center",
        alignItems: "center",
        gap: vertical ? 70 : 110,
        padding: vertical ? "120px 70px" : "0 120px",
      }}
    >
      {copy}
      {device}
    </AbsoluteFill>
  );
};
