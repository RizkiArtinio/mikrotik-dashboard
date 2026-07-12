import { Card, CardContent } from "@mui/material";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { TrafficHistoryPoint } from "@/types/traffic";
import { formatBytes } from "@/utils/format";

export function BandwidthChart({ points }: { points: TrafficHistoryPoint[] }) {
  const data = points.map((p) => ({
    time: new Date(p.timestamp).toLocaleString(),
    rx: p.rx,
    tx: p.tx,
  }));

  return (
    <Card variant="outlined">
      <CardContent>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
            <XAxis dataKey="time" tick={{ fontSize: 11 }} minTickGap={40} />
            <YAxis tickFormatter={(v) => formatBytes(v)} tick={{ fontSize: 11 }} width={90} />
            <Tooltip formatter={(v: number) => formatBytes(v)} />
            <Bar dataKey="rx" name="RX" fill="#1565c0" />
            <Bar dataKey="tx" name="TX" fill="#00897b" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
