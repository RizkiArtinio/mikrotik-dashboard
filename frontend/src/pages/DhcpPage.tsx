import { Alert, Stack, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { LoadingState } from "@/components/common/LoadingState";
import { DhcpLeaseTable } from "@/components/dhcp/DhcpLeaseTable";
import { useRouterSelection } from "@/hooks/useRouterSelection";
import { dhcpApi } from "@/services/dhcpApi";

export default function DhcpPage() {
  const { routerId } = useRouterSelection();
  const { data, isLoading } = useQuery({
    queryKey: ["dhcp-leases", routerId],
    queryFn: () => dhcpApi.leases(routerId as number),
    enabled: routerId !== null,
    refetchInterval: 15000,
  });

  if (routerId === null) return <Alert severity="info">Select a router first.</Alert>;
  if (isLoading) return <LoadingState />;

  return (
    <Stack spacing={3}>
      <Typography variant="h5" fontWeight={700}>
        DHCP Leases
      </Typography>
      <DhcpLeaseTable leases={data?.leases ?? []} />
    </Stack>
  );
}
