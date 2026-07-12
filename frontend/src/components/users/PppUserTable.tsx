import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import type { PppUser } from "@/types/misc";
import { formatBytes } from "@/utils/format";

export function PppUserTable({ users }: { users: PppUser[] }) {
  return (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Username</TableCell>
            <TableCell>Service</TableCell>
            <TableCell>Address</TableCell>
            <TableCell>Login Time</TableCell>
            <TableCell align="right">Bytes In</TableCell>
            <TableCell align="right">Bytes Out</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {users.map((u, idx) => (
            <TableRow key={idx} hover>
              <TableCell>{u.username}</TableCell>
              <TableCell>{u.service ?? "—"}</TableCell>
              <TableCell>{u.address ?? "—"}</TableCell>
              <TableCell>{u.login_time ?? "—"}</TableCell>
              <TableCell align="right">{formatBytes(u.bytes_in)}</TableCell>
              <TableCell align="right">{formatBytes(u.bytes_out)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
