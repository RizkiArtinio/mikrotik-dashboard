import { Alert, Stack, Typography } from "@mui/material";
import Grid from "@mui/material/Grid2";
import { useState } from "react";
import { OvpnCredentialsDisplay } from "@/components/vpn/OvpnCredentialsDisplay";
import { OvpnGeneratorForm } from "@/components/vpn/OvpnGeneratorForm";
import { useRouterSelection } from "@/hooks/useRouterSelection";
import type { OvpnPeerResult } from "@/types/vpn";

export default function OvpnGeneratorPage() {
  const { routerId } = useRouterSelection();
  const [result, setResult] = useState<OvpnPeerResult | null>(null);

  if (routerId === null) return <Alert severity="info">Select a router first.</Alert>;

  return (
    <Stack spacing={3}>
      <Typography variant="h5" fontWeight={700}>
        Create OpenVPN Account
      </Typography>
      <Grid container spacing={4}>
        <Grid size={{ xs: 12, md: 5 }}>
          <OvpnGeneratorForm routerId={routerId} onGenerated={setResult} />
        </Grid>
        <Grid size={{ xs: 12, md: 7 }}>
          {result ? (
            <Stack spacing={2}>
              <Typography variant="subtitle1" fontWeight={700}>
                {result.peer.peer_name} — Connection Details
              </Typography>
              <OvpnCredentialsDisplay result={result} />
            </Stack>
          ) : (
            <Alert severity="info">Isi form dan klik Generate untuk buat akun OpenVPN baru.</Alert>
          )}
        </Grid>
      </Grid>
    </Stack>
  );
}
