import { Alert, MenuItem, Stack, TextField, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { BandwidthChart } from "@/components/bandwidth/BandwidthChart";
import { BandwidthRangeSelector } from "@/components/bandwidth/BandwidthRangeSelector";
import { LoadingState } from "@/components/common/LoadingState";
import { useRouterSelection } from "@/hooks/useRouterSelection";
import { useTrafficHistory } from "@/hooks/useTrafficHistory";
import { interfaceApi } from "@/services/interfaceApi";
import type { BandwidthRange } from "@/types/traffic";

export default function BandwidthPage() {
  const { routerId } = useRouterSelection();
  const [interfaceName, setInterfaceName] = useState<string | null>(null);
  const [range, setRange] = useState<BandwidthRange>("day");

  const { data: interfaces } = useQuery({
    queryKey: ["interfaces", routerId],
    queryFn: () => interfaceApi.list(routerId as number),
    enabled: routerId !== null,
  });

  useEffect(() => {
    if (!interfaceName && interfaces && interfaces.length > 0) {
      setInterfaceName(interfaces[0].interface_name);
    }
  }, [interfaces, interfaceName]);

  const history = useTrafficHistory(routerId, interfaceName, range);

  if (routerId === null) return <Alert severity="info">Select a router first.</Alert>;

  return (
    <Stack spacing={3}>
      <Typography variant="h5" fontWeight={700}>
        Bandwidth History
      </Typography>
      <Stack direction="row" spacing={2} alignItems="center">
        <TextField
          select
          size="small"
          label="Interface"
          value={interfaceName ?? ""}
          onChange={(e) => setInterfaceName(e.target.value)}
          sx={{ minWidth: 200 }}
        >
          {(interfaces ?? []).map((iface) => (
            <MenuItem key={iface.id} value={iface.interface_name}>
              {iface.interface_name}
            </MenuItem>
          ))}
        </TextField>
        <BandwidthRangeSelector value={range} onChange={setRange} />
      </Stack>

      {history.isLoading ? (
        <LoadingState />
      ) : history.data && history.data.points.length > 0 ? (
        <BandwidthChart points={history.data.points} />
      ) : (
        <Alert severity="info">No historical data yet for this range.</Alert>
      )}
    </Stack>
  );
}
