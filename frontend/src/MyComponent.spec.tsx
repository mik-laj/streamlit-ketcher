import {
  FORMAT_MOLFILE,
  FORMAT_SMILES,
  MyComponent,
  MyComponentsArgs,
  MyComponentsProps,
} from "./MyComponent";

import {
  fireEvent,
  queryByText,
  render,
  waitFor,
} from "@testing-library/react";
import { darkTheme } from "./mocks";
import { StreamlitKetcherEditorProps } from "./StreamlitKetcherEditor";
import { Ketcher } from "ketcher-core";
import { Streamlit } from "streamlit-component-lib";

jest.mock("./StreamlitKetcherEditor", () => {
  let currentMolecule: string | null = null;
  let moleculeListener: ((mol: string) => null) | null = null;
  const mockKetcher = {
    setMolecule: (mol: string) => {
      currentMolecule = mol;
      if (moleculeListener) {
        moleculeListener(mol);
      }
    },
    getSmiles: () => "SMILES:" + currentMolecule,
    getMolfile: () => "MOLFILE:" + currentMolecule,
  };

  return {
    __esModule: true,
    default: (props: StreamlitKetcherEditorProps) => {
      const [molecule, setMolecule] = require("react").useState();
      moleculeListener = setMolecule;
      require("react").useEffect(() => {
        const timer = setTimeout(
          () => props.onInit!(mockKetcher as unknown as Ketcher),
          0
        );

        return () => clearTimeout(timer);
      }, []);

      return (
        <div>
          StreamlitKetcherEditor [
          {"molecule=" + JSON.stringify(currentMolecule)}]
        </div>
      );
    },
  };
});

function getArgs(args: Partial<MyComponentsArgs> = {}): MyComponentsArgs {
  return { molecule_format: "SMILES", height: 500, molecule: "CCO", ...args };
}

function getProps(props: Partial<MyComponentsProps> = {}): MyComponentsProps {
  return {
    args: getArgs(),
    disabled: true,
    width: 500,
    theme: darkTheme,
    ...props,
  };
}

describe("MyCompoennt", () => {
  beforeAll(() => {
    jest.spyOn(Streamlit, "setFrameHeight");
    jest.spyOn(Streamlit, "setComponentValue");
  });

  it("should respect height of component and update height of the parent frame ", () => {
    const props = getProps({ args: getArgs({ height: 8000 }) });
    render(<MyComponent {...props} />);

    expect(jest.mocked(Streamlit.setFrameHeight).mock.calls).toHaveLength(1);
  });

  it("component should be disabled initially", () => {
    const props = getProps({ args: getArgs({ height: 8000 }) });

    const { getByTestId, getByRole } = render(<MyComponent {...props} />);

    expect(
      (getByRole("button", { name: "Apply" }) as HTMLButtonElement).disabled
    ).toEqual(true);
    expect(
      (getByRole("button", { name: "Reset" }) as HTMLButtonElement).disabled
    ).toEqual(true);
    expect(getByTestId("loading-placeholder")).toBeVisible();
  });

  it("buttons should be enabled and placeholder should be invisible after ketcher intiialization", async () => {
    const props = getProps({ args: getArgs({ height: 8000 }) });

    const { queryByTestId, getByRole, queryByText } = render(
      <MyComponent {...props} />
    );
    await waitFor(() => {
      expect(
        (getByRole("button", { name: "Apply" }) as HTMLButtonElement).disabled
      ).toEqual(false);
    });

    expect(
      (getByRole("button", { name: "Reset" }) as HTMLButtonElement).disabled
    ).toEqual(false);
    expect(queryByTestId("loading-placeholder")).toBeNull();
    expect(queryByText(/StreamlitKetcherEditor/)).not.toBeNull();
  });

  it("editor should have set molecule after ketcher initialization", async () => {
    const props = getProps({ args: getArgs({ molecule: "NEW_MOLECULE" }) });

    const { getByRole, queryByText } = render(<MyComponent {...props} />);
    await waitFor(() => {
      expect(
        (getByRole("button", { name: "Apply" }) as HTMLButtonElement).disabled
      ).toEqual(false);
    });

    expect(queryByText(/molecule="NEW_MOLECULE"/)).not.toBeNull();
  });

  it("reset buttons should set empty molecule", async () => {
    const props = getProps({ args: getArgs({ molecule: "USER_MOLECULE" }) });

    const { getByRole, queryByText } = render(<MyComponent {...props} />);
    await waitFor(() => {
      expect(
        (getByRole("button", { name: "Apply" }) as HTMLButtonElement).disabled
      ).toEqual(false);
    });
    expect(queryByText(/molecule="USER_MOLECULE"/)).not.toBeNull();
    fireEvent.click(getByRole("button", { name: "Reset" }));

    await waitFor(() => {
      expect(queryByText(/molecule=""/)).not.toBeNull();
    });
  });

  it.each([
    [FORMAT_SMILES, "CCO"],
    [FORMAT_MOLFILE, "CCCCC"],
  ])(
    "apply buttons should set molecule to parent frame",
    async (moleculeFormat, molecule) => {
      const props = getProps({
        args: getArgs({
          height: 800,
          molecule_format: moleculeFormat as unknown as
            | typeof FORMAT_SMILES
            | typeof FORMAT_MOLFILE,
          molecule,
        }),
      });
      const setComponentValueMock = jest.mocked(
        Streamlit.setComponentValue
      ).mock;

      const { getByRole } = render(<MyComponent {...props} />);
      const buttonApply = getByRole("button", {
        name: "Apply",
      }) as HTMLButtonElement;
      await waitFor(() => expect(buttonApply.disabled).toEqual(false));
      fireEvent.click(buttonApply);

      await waitFor(() => expect(setComponentValueMock.calls).toHaveLength(1));
      expect(setComponentValueMock.calls[0][0]).toEqual(
        `${moleculeFormat}:${molecule}`
      );
    }
  );
});
