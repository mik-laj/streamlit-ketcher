import { render } from "@testing-library/react";
import { Button, ButtonContainer } from "./Button";
import { darkTheme } from "./mocks";

describe("Button", () => {
  it("should render component", () => {
    const wrapper = render(<Button theme={darkTheme}>Text</Button>);
    expect(wrapper.baseElement.textContent).toEqual("Text");
  });
});

describe("ButtonContainer", () => {
  it("should render component", () => {
    const { getAllByRole } = render(
      <ButtonContainer>
        <Button theme={darkTheme}>Text 1</Button>
        <Button theme={darkTheme}>Text 2</Button>
      </ButtonContainer>
    );
    expect(getAllByRole("button").length).toEqual(2);
  });
});
