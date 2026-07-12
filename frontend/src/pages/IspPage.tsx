import { Alert, Stack, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { LoadingState } from "@/components/common/LoadingState";
import { IspStatusPanel } from "@/components/isp/IspStatusPanel";
import { useRouterSelection } from "@/hooks/useRouterSelection";
import { ispApi } from "@/services/ispApi";

export default function IspPage() {
  const { routerId } = useRouterSelection();
  const { data, isLoading } = useQuery({
    queryKey: ["isp-status", routerId],
    queryFn: () => ispApi.status(routerId as number),
    enabled: routerId !== null,
    refetchInterval: 10000,
  });

  if (routerId === null) return <Alert severity="info">Select a router first.</Alert>;
  if (isLoading) return <LoadingState />;

  return (
    <Stack spacing={3}>
      <Typography variant="h5" fontWeight={700}>
        ISP Monitoring
      </Typography>
      {data && <IspStatusPanel results={data.results} />}
    </Stack>
  );
}
