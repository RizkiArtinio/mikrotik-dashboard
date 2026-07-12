import { Card, CardContent, Typography } from "@mui/material";
import { useEffect, useRef, useState } from "react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { DashboardSnapshot } from "@/types/dashboard";
import { formatBps } from "@/utils/format";

const MAX_POINTS = 60;

interface Point {
  time: string;
  rx: number;
  tx: number;
}

export function TrafficSummaryChart({ snapshot }: { snapshot: DashboardSnapshot | null }) {
  const [points, setPoints] = useState<Point[]>([]);
  const lastTs = useRef<string | null>(null);

  useEffect(() => {
    if (!snapshot || snapshot.generated_at === lastTs.current) return;
    lastTs.current = snapshot.generated_at;
    setPoints((prev) => {
      const next = [
        ...prev,
        {
          time: new Date(snapshot.generated_at).toLocaleTimeString(),
          rx: snapshot.total_rx_bps,
          tx: snapshot.total_tx_bps,
        },
      ];
      return next.length > MAX_POINTS ? next.slice(next.length - MAX_POINTS) : next;
    });
  }, [snapshot]);

  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="subtitle1" fontWeight={700} gutterBottom>
          Total Bandwidth (live)
        </Typography>
        <ResponsiveContainer width="100%" height={260}>
          <AreaChart data={points}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
            <XAxis dataKey="time" tick={{ fontSize: 11 }} minTickGap={30} />
            <YAxis tickFormatter={(v) => formatBps(v)} tick={{ fontSize: 11 }} width={80} />
            <Tooltip formatter={(v: number) => formatBps(v)} />
            <Area type="monotone" dataKey="rx" name="RX" stroke="#1565c0" fill="#1565c0" fillOpacity={0.25} />
            <Area type="monotone" dataKey="tx" name="TX" stroke="#00897b" fill="#00897b" fillOpacity={0.25} />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
