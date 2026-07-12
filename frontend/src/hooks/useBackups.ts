import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { backupApi } from "@/services/backupApi";

export function useBackups(routerId: number | null) {
  return useQuery({
    queryKey: ["backups", routerId],
    queryFn: () => backupApi.list(routerId as number),
    enabled: routerId !== null,
  });
}

export function useTriggerBackup(routerId: number | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => backupApi.trigger(routerId as number),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["backups", routerId] });
    },
  });
}
