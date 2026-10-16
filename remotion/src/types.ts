// Props written by launchpad/steps/media.py (_remotion_props). Keep both sides in sync.

export type BrandColors = {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  text: string;
};

export type Scene = {
  title: string;
  caption: string;
  image: string; // path under public/ ("runs/<id>/app-desktop-0.png") or "" for a text-only card
};

export type LaunchProps = {
  brandName: string;
  tagline: string;
  hook: string;
  cta: string;
  colors: BrandColors;
  headingFont: string;
  scenes: Scene[];
};

export const FPS = 30;
export const INTRO = 75;
export const SCENE = 120;
export const OUTRO = 90;

export const demoDuration = (p: LaunchProps) => INTRO + Math.max(p.scenes.length, 1) * SCENE + OUTRO;

export const defaultProps: LaunchProps = {
  brandName: "Ledgerly",
  tagline: "Get paid on time, every time",
  hook: "Chasing invoices again this week?",
  cta: "Start free at ledgerly.app",
  colors: { primary: "#1F4FFF", secondary: "#0B1B3F", accent: "#FFB224", background: "#F6F7FB", text: "#0B1B3F" },
  headingFont: "Space Grotesk",
  scenes: [
    { title: "Invoices in 30 seconds", caption: "Pick a client, add line items, send.", image: "" },
    { title: "Automatic reminders", caption: "Polite nudges go out before and after the due date.", image: "" },
    { title: "See who owes what", caption: "One dashboard for paid, due and overdue.", image: "" },
  ],
};
