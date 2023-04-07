import { Theme } from "streamlit-component-lib";

// streamlit-component-lib miss some fields
interface FixedTheme extends Theme {
  primaryColor: string;
  backgroundColor: string;
  secondaryBackgroundColor: string;
  textColor: string;
  base: string;
  font: string;
  linkText: string;
  fadedText05: string;
  fadedText10: string;
  fadedText20: string;
  fadedText40: string;
  fadedText60: string;
  bgMix: string;
  darkenedBgMix100: string;
  darkenedBgMix25: string;
  darkenedBgMix15: string;
  lightenedBg05: string;
}
