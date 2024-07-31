// NOTE: The following line needs to be the first import to ensure that we
// correctly configure where chunked static assets are fetched from.
import "./setWebpackPublicPath"

import * as React from "react";
import * as ReactDOM from "react-dom";
import "./index.css";
import MyComponent from "./MyComponent";

ReactDOM.render(
  <React.StrictMode>
    <MyComponent />
  </React.StrictMode>,
  document.getElementById("root")
);
