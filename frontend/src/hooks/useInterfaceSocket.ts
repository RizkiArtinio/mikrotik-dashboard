import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { interfaceApi } from "@/services/interfaceApi";
import { ReconnectingSocket } from "@/services/wsClient";
import type { InterfaceItem } from "@/types/interface";
import type { InterfaceUpdateEvent } from "@/types/ws-events";

export function useInterfaceSocket(routerId: number | null) {
  const [interfaces, setInterfaces] = useState<InterfaceItem[]>([]);
  const [wsConnected, setWsConnected] = useState(false);
  const socketRef = useRef<ReconnectingSocket | null>(null);

  useEffect(() => {
    if (routerId === null) return;

    const socket = new ReconnectingSocket(
      `/interfaces/${routerId}`,
      (raw) => {
        const event = raw as InterfaceUpdateEvent;
        if (event.type === "interface_update") {
          setInterfaces(event.data);
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

  const fallback = useQuery({
    queryKey: ["interfaces-fallback", routerId],
    queryFn: () => interfaceApi.list(routerId as number),
    enabled: routerId !== null && !wsConnected,
    refetchInterval: 5000,
  });

  useEffect(() => {
    if (!wsConnected && fallback.data) {
      setInterfaces(fallback.data);
    }
  }, [wsConnected, fallback.data]);

  return { interfaces, connected: wsConnected };
}
