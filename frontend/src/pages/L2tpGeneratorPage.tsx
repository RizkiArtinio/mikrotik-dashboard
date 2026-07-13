import { Alert, Stack, Typography } from "@mui/material";
import Grid from "@mui/material/Grid2";
import { useState } from "react";
import { L2tpCredentialsDisplay } from "@/components/vpn/L2tpCredentialsDisplay";
import { L2tpGeneratorForm } from "@/components/vpn/L2tpGeneratorForm";
import { useRouterSelection } from "@/hooks/useRouterSelection";
import type { L2tpPeerResult } from "@/types/vpn";

export default function L2tpGeneratorPage() {
  const { routerId } = useRouterSelection();
  const [result, setResult] = useState<L2tpPeerResult | null>(null);

  if (routerId === null) return <Alert severity="info">Select a router first.</Alert>;

  return (
    <Stack spacing={3}>
      <Typography variant="h5" fontWeight={700}>
        Create L2TP/IPsec Account
      </Typography>
      <Grid container spacing={4}>
        <Grid size={{ xs: 12, md: 5 }}>
          <L2tpGeneratorForm routerId={routerId} onGenerated={setResult} />
        </Grid>
        <Grid size={{ xs: 12, md: 7 }}>
          {result ? (
            <Stack spacing={2}>
              <Typography variant="subtitle1" fontWeight={700}>
                {result.peer.peer_name} — Connection Details
              </Typography>
              <L2tpCredentialsDisplay result={result} />
            </Stack>
          ) : (
            <Alert severity="info">Isi form dan klik Generate untuk buat akun L2TP baru.</Alert>
          )}
        </Grid>
      </Grid>
    </Stack>
  );
}
