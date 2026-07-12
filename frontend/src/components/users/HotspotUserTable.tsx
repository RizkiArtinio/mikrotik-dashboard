import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import type { HotspotUser } from "@/types/misc";
import { formatBytes } from "@/utils/format";

export function HotspotUserTable({ users }: { users: HotspotUser[] }) {
  return (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Username</TableCell>
            <TableCell>MAC Address</TableCell>
            <TableCell>Address</TableCell>
            <TableCell>Login Time</TableCell>
            <TableCell>Uptime</TableCell>
            <TableCell align="right">Bytes In</TableCell>
            <TableCell align="right">Bytes Out</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {users.map((u, idx) => (
            <TableRow key={idx} hover>
              <TableCell>{u.username}</TableCell>
              <TableCell>{u.mac_address ?? "—"}</TableCell>
              <TableCell>{u.address ?? "—"}</TableCell>
              <TableCell>{u.login_time ?? "—"}</TableCell>
              <TableCell>{u.uptime ?? "—"}</TableCell>
              <TableCell align="right">{formatBytes(u.bytes_in)}</TableCell>
              <TableCell align="right">{formatBytes(u.bytes_out)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
