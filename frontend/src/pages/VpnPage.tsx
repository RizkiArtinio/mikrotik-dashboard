import { Alert, Stack, Typography } from "@mui/material";
import { LoadingState } from "@/components/common/LoadingState";
import { VpnPeerTable } from "@/components/vpn/VpnPeerTable";
import { useRouterSelection } from "@/hooks/useRouterSelection";
import { useVpnPeers } from "@/hooks/useVpnPeers";

export default function VpnPage() {
  const { routerId } = useRouterSelection();
  const { data: peers, isLoading } = useVpnPeers(routerId);

  if (routerId === null) return <Alert severity="info">Select a router first.</Alert>;
  if (isLoading) return <LoadingState />;

  return (
    <Stack spacing={3}>
      <Typography variant="h5" fontWeight={700}>
        VPN Status
      </Typography>
      {!peers || peers.length === 0 ? (
        <Alert severity="info">No VPN peers configured yet.</Alert>
      ) : (
        <VpnPeerTable peers={peers} />
      )}
    </Stack>
  );
}
