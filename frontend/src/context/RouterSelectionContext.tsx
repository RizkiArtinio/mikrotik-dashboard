import { createContext, useEffect, useState, type ReactNode } from "react";

interface RouterSelectionContextValue {
  routerId: number | null;
  setRouterId: (id: number) => void;
}

export const RouterSelectionContext = createContext<RouterSelectionContextValue | undefined>(undefined);

export function RouterSelectionProvider({ children }: { children: ReactNode }) {
  const [routerId, setRouterIdState] = useState<number | null>(() => {
    const stored = localStorage.getItem("selected_router_id");
    return stored ? Number(stored) : null;
  });

  useEffect(() => {
    if (routerId !== null) {
      localStorage.setItem("selected_router_id", String(routerId));
    }
  }, [routerId]);

  const setRouterId = (id: number) => setRouterIdState(id);

  return (
    <RouterSelectionContext.Provider value={{ routerId, setRouterId }}>
      {children}
    </RouterSelectionContext.Provider>
  );
}
