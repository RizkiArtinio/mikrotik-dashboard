import {
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import type { InterfaceItem } from "@/types/interface";
import { formatBps } from "@/utils/format";

export function InterfaceTable({ interfaces }: { interfaces: InterfaceItem[] }) {
  return (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Interface</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Status</TableCell>
            <TableCell align="right">RX</TableCell>
            <TableCell align="right">TX</TableCell>
            <TableCell align="right">RX Packets</TableCell>
            <TableCell align="right">TX Packets</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {interfaces.map((iface) => (
            <TableRow key={iface.id} hover>
              <TableCell>{iface.interface_name}</TableCell>
              <TableCell>{iface.interface_type}</TableCell>
              <TableCell>
                <Chip
                  size="small"
                  label={iface.status}
                  color={iface.status === "running" ? "success" : "default"}
                />
              </TableCell>
              <TableCell align="right">{formatBps(iface.rx_bps)}</TableCell>
              <TableCell align="right">{formatBps(iface.tx_bps)}</TableCell>
              <TableCell align="right">{iface.rx_packets.toLocaleString()}</TableCell>
              <TableCell align="right">{iface.tx_packets.toLocaleString()}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
