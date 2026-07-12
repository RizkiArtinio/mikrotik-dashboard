import { Box, Paper, Typography } from "@mui/material";

export function QrCodeDisplay({ base64Png }: { base64Png: string }) {
  return (
    <Paper variant="outlined" sx={{ p: 2, textAlign: "center", display: "inline-block" }}>
      <Box component="img" src={`data:image/png;base64,${base64Png}`} alt="WireGuard QR code" width={220} height={220} />
      <Typography variant="caption" display="block" color="text.secondary" mt={1}>
        Scan with the WireGuard mobile app
      </Typography>
    </Paper>
  );
}
