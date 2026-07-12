import { Alert, Chip, Stack, Typography } from "@mui/material";
import { ConnectionStatusBadge } from "@/components/common/ConnectionStatusBadge";
import { LoadingState } from "@/components/common/LoadingState";
import { QuickStats } from "@/components/dashboard/QuickStats";
import { ResourceGauges } from "@/components/dashboard/ResourceGauges";
import { TrafficSummaryChart } from "@/components/dashboard/TrafficSummaryChart";
import { useDashboardSocket } from "@/hooks/useDashboardSocket";
import { useRouterSelection } from "@/hooks/useRouterSelection";

export default function DashboardPage() {
  const { routerId } = useRouterSelection();
  const { snapshot, connected } = useDashboardSocket(routerId);

  if (routerId === null) return <Alert severity="info">Add a router in Admin → Routers to get started.</Alert>;
  if (!snapshot) return <LoadingState label="Waiting for router data..." />;

  return (
    <Stack spacing={3}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Stack direction="row" spacing={2} alignItems="center">
          <Typography variant="h5" fontWeight={700}>
            {snapshot.router_name}
          </Typography>
          <Chip
            label={snapshot.online ? "Online" : "Offline"}
            color={snapshot.online ? "success" : "error"}
          />
          {snapshot.uptime && <Typography color="text.secondary">Uptime: {snapshot.uptime}</Typography>}
        </Stack>
        <ConnectionStatusBadge connected={connected} />
      </Stack>

      {!snapshot.online && <Alert severity="error">{snapshot.error ?? "Router is unreachable"}</Alert>}

      <QuickStats snapshot={snapshot} />
      <ResourceGauges resources={snapshot.resources} health={snapshot.health} />
      <TrafficSummaryChart snapshot={snapshot} />
    </Stack>
  );
}
