import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import DownloadIcon from "@mui/icons-material/Download";
import { Button, IconButton, Paper, Stack, Typography } from "@mui/material";
import type { OvpnPeerResult } from "@/types/vpn";

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

export function OvpnCredentialsDisplay({ result }: { result: OvpnPeerResult }) {
  const handleDownload = () => {
    const blob = new Blob([result.config_text], { type: "application/x-openvpn-profile" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${result.peer.peer_name}.ovpn`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Stack spacing={2}>
      <Paper variant="outlined" sx={{ p: 2 }}>
        <Stack spacing={1.5}>
          <CredentialRow label="Username" value={result.username} />
          <CredentialRow label="Password" value={result.password} />
        </Stack>
      </Paper>
      <Stack direction="row" spacing={1}>
        <Button startIcon={<DownloadIcon />} onClick={handleDownload} variant="contained" size="small">
          Download .ovpn
        </Button>
      </Stack>
      <Paper variant="outlined" sx={{ p: 2, bgcolor: "grey.50" }}>
        <Typography variant="subtitle2" gutterBottom>
          Cara pakai
        </Typography>
        <Typography variant="body2" color="text.secondary" component="div">
          Install app <b>OpenVPN Connect</b> (Android/iOS/Desktop) → Import Profile → pilih file{" "}
          <code>{result.peer.peer_name}.ovpn</code> yang baru diunduh → saat connect, masukkan Username dan
          Password di atas.
        </Typography>
      </Paper>
    </Stack>
  );
}
