import { StandaloneStructServiceProvider } from "ketcher-standalone";
import { Editor as KetcherEditor } from "ketcher-react";
import styled from "@emotion/styled";
import { Config } from "ketcher-react/dist/script";
import { Ketcher } from "ketcher-core";

interface KetcherEditorWrapperProps {
  height: number;
}

const KetcherEditorWrapper = styled.div<KetcherEditorWrapperProps>((props) => ({
  height: `${props.height}px`,
}));

KetcherEditorWrapper.defaultProps = {
  // TypeScript has trouble detecting types here because it's a static field.
  // @ts-ignore
  height: "500",
};

const structServiceProvider = new StandaloneStructServiceProvider();

export interface StreamlitKetcherEditorProps
  extends Omit<
    Config,
    "element" | "staticResourcesUrl" | "structServiceProvider"
  > {
  onInit?: (ketcher: Ketcher) => void;
  height: number;
}

export const StreamlitKetcherEditor = ({
  height,
  ...rest
}: StreamlitKetcherEditorProps) => (
  <KetcherEditorWrapper height={height}>
    <KetcherEditor
      staticResourcesUrl={process.env.PUBLIC_URL!}
      structServiceProvider={structServiceProvider}
      {...rest}
    />
  </KetcherEditorWrapper>
);

export default StreamlitKetcherEditor;
