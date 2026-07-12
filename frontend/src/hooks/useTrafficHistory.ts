import { useQuery } from "@tanstack/react-query";
import { trafficApi } from "@/services/trafficApi";
import type { BandwidthRange } from "@/types/traffic";

export function useTrafficHistory(routerId: number | null, interfaceName: string | null, range: BandwidthRange) {
  return useQuery({
    queryKey: ["traffic-history", routerId, interfaceName, range],
    queryFn: () => trafficApi.getHistory(routerId as number, interfaceName as string, range),
    enabled: routerId !== null && !!interfaceName,
  });
}
