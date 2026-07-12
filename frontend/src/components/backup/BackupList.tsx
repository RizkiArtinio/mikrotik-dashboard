import DownloadIcon from "@mui/icons-material/Download";
import {
  Chip,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import { backupApi } from "@/services/backupApi";
import type { BackupItem } from "@/types/backup";
import { formatBytes } from "@/utils/format";

export function BackupList({ backups }: { backups: BackupItem[] }) {
  return (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>File</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Trigger</TableCell>
            <TableCell align="right">Size</TableCell>
            <TableCell>Date</TableCell>
            <TableCell align="right">Download</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {backups.map((b) => (
            <TableRow key={b.id} hover>
              <TableCell>{b.file_name}</TableCell>
              <TableCell>
                <Chip size="small" label={b.backup_type} />
              </TableCell>
              <TableCell>{b.triggered_by}</TableCell>
              <TableCell align="right">{formatBytes(b.file_size)}</TableCell>
              <TableCell>{new Date(b.backup_date).toLocaleString()}</TableCell>
              <TableCell align="right">
                <IconButton size="small" onClick={() => backupApi.download(b.id, b.file_name)}>
                  <DownloadIcon fontSize="small" />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
