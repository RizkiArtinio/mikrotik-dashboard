import { useContext } from "react";
import { RouterSelectionContext } from "@/context/RouterSelectionContext";

export function useRouterSelection() {
  const ctx = useContext(RouterSelectionContext);
  if (!ctx) throw new Error("useRouterSelection must be used within RouterSelectionProvider");
  return ctx;
}
