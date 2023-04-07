import { render } from "@testing-library/react";
import React from "react";
import { EmptySpace, LoadingPlaceholder } from "./LoadingPlaceholder";

describe("LoadingPlaceholder", () => {
  it("should render component", () => {
    const wrapper = render(<LoadingPlaceholder height={420} />);
    const el = wrapper.container.children[0];
    const styles = window.getComputedStyle(el);
    expect(styles.height).toBe("420px");
  });
});

describe("EmptySpace", () => {
  it("should render component", () => {
    const wrapper = render(<EmptySpace height={420} />);
    const el = wrapper.container.children[0];
    const styles = window.getComputedStyle(el);
    expect(styles.height).toBe("420px");
  });
});
