import { Alert, Stack, Tab, Tabs, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { LoadingState } from "@/components/common/LoadingState";
import { HotspotUserTable } from "@/components/users/HotspotUserTable";
import { PppUserTable } from "@/components/users/PppUserTable";
import { useRouterSelection } from "@/hooks/useRouterSelection";
import { pppHotspotApi } from "@/services/pppHotspotApi";

export default function UsersActivityPage() {
  const { routerId } = useRouterSelection();
  const [tab, setTab] = useState<"ppp" | "hotspot">("ppp");

  const pppQuery = useQuery({
    queryKey: ["ppp-users", routerId],
    queryFn: () => pppHotspotApi.pppUsers(routerId as number),
    enabled: routerId !== null && tab === "ppp",
    refetchInterval: 10000,
  });
  const hotspotQuery = useQuery({
    queryKey: ["hotspot-users", routerId],
    queryFn: () => pppHotspotApi.hotspotUsers(routerId as number),
    enabled: routerId !== null && tab === "hotspot",
    refetchInterval: 10000,
  });

  if (routerId === null) return <Alert severity="info">Select a router first.</Alert>;

  return (
    <Stack spacing={3}>
      <Typography variant="h5" fontWeight={700}>
        PPP / Hotspot Users
      </Typography>
      <Tabs value={tab} onChange={(_, v) => setTab(v)}>
        <Tab label="PPP Users" value="ppp" />
        <Tab label="Hotspot Users" value="hotspot" />
      </Tabs>
      {tab === "ppp" ? (
        pppQuery.isLoading ? <LoadingState /> : <PppUserTable users={pppQuery.data ?? []} />
      ) : hotspotQuery.isLoading ? (
        <LoadingState />
      ) : (
        <HotspotUserTable users={hotspotQuery.data ?? []} />
      )}
    </Stack>
  );
}
