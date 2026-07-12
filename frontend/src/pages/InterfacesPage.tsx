import { Alert, Stack, Typography } from "@mui/material";
import { ConnectionStatusBadge } from "@/components/common/ConnectionStatusBadge";
import { InterfaceRealtimeChart } from "@/components/interfaces/InterfaceRealtimeChart";
import { InterfaceTable } from "@/components/interfaces/InterfaceTable";
import { useInterfaceSocket } from "@/hooks/useInterfaceSocket";
import { useRouterSelection } from "@/hooks/useRouterSelection";

export default function InterfacesPage() {
  const { routerId } = useRouterSelection();
  const { interfaces, connected } = useInterfaceSocket(routerId);

  if (routerId === null) return <Alert severity="info">Select a router first.</Alert>;

  return (
    <Stack spacing={3}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="h5" fontWeight={700}>
          Interfaces
        </Typography>
        <ConnectionStatusBadge connected={connected} />
      </Stack>
      {interfaces.length === 0 ? (
        <Alert severity="info">No interface data yet — waiting for first poll.</Alert>
      ) : (
        <>
          <InterfaceRealtimeChart interfaces={interfaces} />
          <InterfaceTable interfaces={interfaces} />
        </>
      )}
    </Stack>
  );
}
