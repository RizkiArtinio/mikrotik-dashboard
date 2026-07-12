import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import type { DhcpLease } from "@/types/misc";

export function DhcpLeaseTable({ leases }: { leases: DhcpLease[] }) {
  return (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Hostname</TableCell>
            <TableCell>MAC Address</TableCell>
            <TableCell>IP Address</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Expires After</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {leases.map((lease, idx) => (
            <TableRow key={idx} hover>
              <TableCell>{lease.hostname ?? "—"}</TableCell>
              <TableCell>{lease.mac_address ?? "—"}</TableCell>
              <TableCell>{lease.ip_address ?? "—"}</TableCell>
              <TableCell>{lease.status ?? "—"}</TableCell>
              <TableCell>{lease.expires_after ?? "—"}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
