import { useQuery } from "@tanstack/react-query";
import { routerApi } from "@/services/routerApi";

export function useRouters() {
  return useQuery({ queryKey: ["routers"], queryFn: routerApi.list });
}
