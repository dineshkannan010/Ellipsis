import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { MacbookAir } from "./screens/MacbookAir";

createRoot(document.getElementById("app") as HTMLElement).render(
  <StrictMode>
    <MacbookAir />
  </StrictMode>,
);
