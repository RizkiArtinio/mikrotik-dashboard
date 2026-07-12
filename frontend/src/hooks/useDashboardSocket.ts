import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { dashboardApi } from "@/services/dashboardApi";
import { ReconnectingSocket } from "@/services/wsClient";
import type { DashboardSnapshot } from "@/types/dashboard";
import type { DashboardUpdateEvent } from "@/types/ws-events";

export function useDashboardSocket(routerId: number | null) {
  const [snapshot, setSnapshot] = useState<DashboardSnapshot | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const socketRef = useRef<ReconnectingSocket | null>(null);

  useEffect(() => {
    if (routerId === null) return;

    const socket = new ReconnectingSocket(
      `/dashboard/${routerId}`,
      (raw) => {
        const event = raw as DashboardUpdateEvent;
        if (event.type === "dashboard_update") {
          setSnapshot(event.data);
        }
      },
      setWsConnected,
    );
    socketRef.current = socket;
    socket.connect();

    return () => {
      socket.close();
      socketRef.current = null;
      setWsConnected(false);
    };
  }, [routerId]);

  // REST fallback: keeps data fresh via polling if the WebSocket is down.
  const fallback = useQuery({
    queryKey: ["dashboard-fallback", routerId],
    queryFn: () => dashboardApi.get(routerId as number),
    enabled: routerId !== null && !wsConnected,
    refetchInterval: 5000,
  });

  useEffect(() => {
    if (!wsConnected && fallback.data) {
      setSnapshot(fallback.data);
    }
  }, [wsConnected, fallback.data]);

  return { snapshot, connected: wsConnected };
}
