import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import type { FirewallRuleStat } from "@/types/misc";

export function FirewallStatsTable({ rules }: { rules: FirewallRuleStat[] }) {
  return (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Chain</TableCell>
            <TableCell>Action</TableCell>
            <TableCell>Comment</TableCell>
            <TableCell align="right">Bytes</TableCell>
            <TableCell align="right">Packets</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rules.map((rule, idx) => (
            <TableRow key={idx} hover>
              <TableCell>{rule.chain}</TableCell>
              <TableCell>{rule.action}</TableCell>
              <TableCell>{rule.comment ?? "—"}</TableCell>
              <TableCell align="right">{rule.bytes.toLocaleString()}</TableCell>
              <TableCell align="right">{rule.packets.toLocaleString()}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
