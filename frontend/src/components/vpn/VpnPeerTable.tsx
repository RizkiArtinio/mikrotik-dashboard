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
import type { VpnPeer } from "@/types/vpn";
import { formatBytes } from "@/utils/format";

const STATUS_COLOR: Record<VpnPeer["status"], "success" | "default" | "warning"> = {
  connected: "success",
  configured: "warning",
  disconnected: "default",
  unknown: "default",
};

export function VpnPeerTable({ peers }: { peers: VpnPeer[] }) {
  return (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Peer Name</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Remote Address</TableCell>
            <TableCell>Status</TableCell>
            <TableCell align="right">RX</TableCell>
            <TableCell align="right">TX</TableCell>
            <TableCell>Last Seen</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {peers.map((peer) => (
            <TableRow key={peer.id} hover>
              <TableCell>{peer.peer_name}</TableCell>
              <TableCell>{peer.vpn_type}</TableCell>
              <TableCell>{peer.remote_address ?? "—"}</TableCell>
              <TableCell>
                <Chip size="small" label={peer.status} color={STATUS_COLOR[peer.status]} />
              </TableCell>
              <TableCell align="right">{formatBytes(peer.rx_bytes)}</TableCell>
              <TableCell align="right">{formatBytes(peer.tx_bytes)}</TableCell>
              <TableCell>{peer.last_seen ? new Date(peer.last_seen).toLocaleString() : "—"}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
