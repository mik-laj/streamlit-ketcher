import styled from "@emotion/styled";
import { transparentize } from "color2k";
import { FixedTheme } from "./Theme";

interface ButtonProps {
  theme: FixedTheme;
}

export const Button = styled.button<ButtonProps>(({ theme }) => ({
  // StyledBaseButton styles
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  // fontWeight: theme.fontWeights.normal,
  fontWeight: 400,
  // padding: `${theme.spacing.xs} ${theme.spacing.md}`,
  padding: "0.25rem 0.75rem",
  // borderRadius: theme.radii.md,
  borderRadius: "0.25rem",
  margin: 0,
  // lineHeight: theme.lineHeights.base,
  lineHeight: 1.6,
  color: "inherit",
  // width: fluidWidth ? "100%" : "auto",
  width: "auto",
  userSelect: "none",
  "&:focus": {
    boxShadow: `0 0 0 0.2rem ${transparentize(theme.primaryColor, 0.5)}`,
    outline: "none",
  },

  // StyledSecondaryButton styles
  backgroundColor: theme.lightenedBg05,
  border: `1px solid ${theme.fadedText10}`,
  "&:hover": {
    borderColor: theme.primaryColor,
    color: theme.primaryColor,
  },
  "&:active": {
    color: "white",
    borderColor: theme.primaryColor,
    backgroundColor: theme.primaryColor,
  },
  "&:focus:not(:active)": {
    borderColor: theme.primaryColor,
    color: theme.primaryColor,
  },
  "&:disabled, &:disabled:hover, &:disabled:active": {
    borderColor: theme.fadedText10,
    backgroundColor: "transparent",
    color: theme.fadedText40,
    cursor: "not-allowed",
  },
}));
export const ButtonContainer = styled.div(() => ({
  display: "flex",
  justifyContent: "space-between",
  padding: "1rem 0",
}));
