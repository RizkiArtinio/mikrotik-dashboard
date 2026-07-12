import { Box, CircularProgress, Typography } from "@mui/material";

export function LoadingState({ label = "Loading..." }: { label?: string }) {
  return (
    <Box display="flex" flexDirection="column" alignItems="center" gap={2} py={6}>
      <CircularProgress size={32} />
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
    </Box>
  );
}
