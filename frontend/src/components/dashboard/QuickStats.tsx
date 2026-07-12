import DownloadIcon from "@mui/icons-material/Download";
import GroupIcon from "@mui/icons-material/Group";
import UploadIcon from "@mui/icons-material/Upload";
import VpnKeyIcon from "@mui/icons-material/VpnKey";
import Grid from "@mui/material/Grid2";
import { StatusCard } from "@/components/dashboard/StatusCard";
import type { DashboardSnapshot } from "@/types/dashboard";
import { formatBps } from "@/utils/format";

export function QuickStats({ snapshot }: { snapshot: DashboardSnapshot }) {
  return (
    <Grid container spacing={2}>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatusCard label="Total RX" value={formatBps(snapshot.total_rx_bps)} icon={<DownloadIcon />} />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatusCard label="Total TX" value={formatBps(snapshot.total_tx_bps)} icon={<UploadIcon />} />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatusCard label="Active VPN Peers" value={snapshot.active_vpn_count} icon={<VpnKeyIcon />} />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatusCard label="Active Users" value={snapshot.active_user_count} icon={<GroupIcon />} />
      </Grid>
    </Grid>
  );
}
