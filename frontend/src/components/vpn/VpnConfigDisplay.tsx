import DownloadIcon from "@mui/icons-material/Download";
import { Button, Paper, Stack } from "@mui/material";

export function VpnConfigDisplay({ configText, peerName }: { configText: string; peerName: string }) {
  const handleDownload = () => {
    const blob = new Blob([configText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${peerName}.conf`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Stack spacing={1}>
      <Paper
        variant="outlined"
        sx={{ p: 2, fontFamily: "monospace", fontSize: 13, whiteSpace: "pre-wrap", bgcolor: "grey.50" }}
      >
        {configText}
      </Paper>
      <Stack direction="row" spacing={1}>
        <Button size="small" startIcon={<DownloadIcon />} onClick={handleDownload}>
          Download .conf
        </Button>
        <Button size="small" onClick={() => navigator.clipboard.writeText(configText)}>
          Copy
        </Button>
      </Stack>
    </Stack>
  );
}
