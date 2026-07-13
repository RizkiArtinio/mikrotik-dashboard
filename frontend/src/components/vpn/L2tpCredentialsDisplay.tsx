import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { IconButton, Paper, Stack, Typography } from "@mui/material";
import type { L2tpPeerResult } from "@/types/vpn";

function CredentialRow({ label, value }: { label: string; value: string }) {
  return (
    <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={2}>
      <Stack>
        <Typography variant="caption" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="body1" fontFamily="monospace">
          {value}
        </Typography>
      </Stack>
      <IconButton size="small" onClick={() => navigator.clipboard.writeText(value)}>
        <ContentCopyIcon fontSize="small" />
      </IconButton>
    </Stack>
  );
}

export function L2tpCredentialsDisplay({ result }: { result: L2tpPeerResult }) {
  return (
    <Stack spacing={2}>
      <Paper variant="outlined" sx={{ p: 2 }}>
        <Stack spacing={1.5}>
          <CredentialRow label="Server" value={result.server_address} />
          <CredentialRow label="Username" value={result.username} />
          <CredentialRow label="Password" value={result.password} />
          <CredentialRow label="IPsec Pre-shared Key" value={result.ipsec_psk ?? "—"} />
        </Stack>
      </Paper>
      <Paper variant="outlined" sx={{ p: 2, bgcolor: "grey.50" }}>
        <Typography variant="subtitle2" gutterBottom>
          Cara setting di HP (Android/iPhone, tanpa app tambahan)
        </Typography>
        <Typography variant="body2" color="text.secondary" component="div">
          Settings → Network/VPN → Tambah VPN → Tipe <b>L2TP/IPSec PSK</b> → isi Server, Username,
          Password, dan IPsec pre-shared key sesuai di atas → Simpan → Connect.
        </Typography>
      </Paper>
    </Stack>
  );
}
