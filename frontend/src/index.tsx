import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { HomePage } from "./Screens/HomePage";

createRoot(document.getElementById("app") as HTMLElement).render(
  <StrictMode>
    <HomePage />
  </StrictMode>,
);
