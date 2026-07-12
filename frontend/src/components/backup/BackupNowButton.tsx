import BackupIcon from "@mui/icons-material/Backup";
import { Button } from "@mui/material";
import { useTriggerBackup } from "@/hooks/useBackups";

export function BackupNowButton({ routerId }: { routerId: number }) {
  const mutation = useTriggerBackup(routerId);

  return (
    <Button
      variant="contained"
      startIcon={<BackupIcon />}
      disabled={mutation.isPending}
      onClick={() => mutation.mutate()}
    >
      {mutation.isPending ? "Backing up..." : "Backup Now"}
    </Button>
  );
}
