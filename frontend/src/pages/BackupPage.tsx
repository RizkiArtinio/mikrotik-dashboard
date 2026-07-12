import { Alert, Stack, Typography } from "@mui/material";
import { BackupList } from "@/components/backup/BackupList";
import { BackupNowButton } from "@/components/backup/BackupNowButton";
import { LoadingState } from "@/components/common/LoadingState";
import { useBackups } from "@/hooks/useBackups";
import { useRouterSelection } from "@/hooks/useRouterSelection";

export default function BackupPage() {
  const { routerId } = useRouterSelection();
  const { data: backups, isLoading } = useBackups(routerId);

  if (routerId === null) return <Alert severity="info">Select a router first.</Alert>;

  return (
    <Stack spacing={3}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="h5" fontWeight={700}>
          Backups
        </Typography>
        <BackupNowButton routerId={routerId} />
      </Stack>
      {isLoading ? (
        <LoadingState />
      ) : !backups || backups.length === 0 ? (
        <Alert severity="info">No backups yet. Click "Backup Now" or wait for the daily schedule.</Alert>
      ) : (
        <BackupList backups={backups} />
      )}
    </Stack>
  );
}
