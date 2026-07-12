import { Alert, Stack, Tab, Tabs, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { LoadingState } from "@/components/common/LoadingState";
import { FirewallStatsTable } from "@/components/firewall/FirewallStatsTable";
import { useRouterSelection } from "@/hooks/useRouterSelection";
import { firewallApi } from "@/services/firewallApi";

export default function FirewallPage() {
  const { routerId } = useRouterSelection();
  const [tab, setTab] = useState<"filter" | "nat">("filter");

  const filterQuery = useQuery({
    queryKey: ["firewall-filter", routerId],
    queryFn: () => firewallApi.filterStats(routerId as number),
    enabled: routerId !== null && tab === "filter",
  });
  const natQuery = useQuery({
    queryKey: ["firewall-nat", routerId],
    queryFn: () => firewallApi.natStats(routerId as number),
    enabled: routerId !== null && tab === "nat",
  });

  if (routerId === null) return <Alert severity="info">Select a router first.</Alert>;

  const activeQuery = tab === "filter" ? filterQuery : natQuery;

  return (
    <Stack spacing={3}>
      <Typography variant="h5" fontWeight={700}>
        Firewall Monitoring
      </Typography>
      <Tabs value={tab} onChange={(_, v) => setTab(v)}>
        <Tab label="Filter Rules" value="filter" />
        <Tab label="NAT Rules" value="nat" />
      </Tabs>
      {activeQuery.isLoading ? (
        <LoadingState />
      ) : (
        <FirewallStatsTable rules={activeQuery.data?.rules ?? []} />
      )}
    </Stack>
  );
}
