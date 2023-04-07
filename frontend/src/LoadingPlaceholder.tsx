import styled from "@emotion/styled";

interface LoadingPlaceholderProps {
  height: number;
}

export const LoadingPlaceholder = styled.div<LoadingPlaceholderProps>(
  (props) => ({
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: `${props.height}px`,
    background: "white",
    color: "#333",
    position: "absolute",
    width: "100%",
    zIndex: 1,
  })
);

export const EmptySpace = styled.div<LoadingPlaceholderProps>((props) => ({
  height: `${props.height}px`,
  width: "100%",
}));
