import { CalculateMetadataFunction, Composition } from "remotion";
import { HeroLoop } from "./HeroLoop";
import { ProductDemo } from "./ProductDemo";
import { defaultProps, demoDuration, FPS, LaunchProps } from "./types";

const fitToScenes: CalculateMetadataFunction<LaunchProps> = ({ props }) => ({
  durationInFrames: demoDuration(props),
});

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="ProductDemo"
      component={ProductDemo}
      width={1920}
      height={1080}
      fps={FPS}
      durationInFrames={demoDuration(defaultProps)}
      defaultProps={defaultProps}
      calculateMetadata={fitToScenes}
    />
    <Composition
      id="ProductDemoVertical"
      component={ProductDemo}
      width={1080}
      height={1920}
      fps={FPS}
      durationInFrames={demoDuration(defaultProps)}
      defaultProps={defaultProps}
      calculateMetadata={fitToScenes}
    />
    <Composition
      id="HeroLoop"
      component={HeroLoop}
      width={1920}
      height={1080}
      fps={FPS}
      durationInFrames={FPS * 8}
      defaultProps={defaultProps}
    />
  </>
);
