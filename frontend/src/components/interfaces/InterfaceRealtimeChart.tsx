import { Card, CardContent, MenuItem, Stack, TextField, Typography } from "@mui/material";
import { useEffect, useRef, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { InterfaceItem } from "@/types/interface";
import { formatBps } from "@/utils/format";

const MAX_POINTS = 60;

interface Point {
  time: string;
  rx: number;
  tx: number;
}

export function InterfaceRealtimeChart({ interfaces }: { interfaces: InterfaceItem[] }) {
  const [selected, setSelected] = useState<string>(interfaces[0]?.interface_name ?? "");
  const [history, setHistory] = useState<Record<string, Point[]>>({});
  const lastUpdatedAt = useRef<Record<string, string>>({});

  useEffect(() => {
    if (!selected && interfaces.length > 0) {
      setSelected(interfaces[0].interface_name);
    }
  }, [interfaces, selected]);

  useEffect(() => {
    setHistory((prev) => {
      const next = { ...prev };
      for (const iface of interfaces) {
        if (lastUpdatedAt.current[iface.interface_name] === iface.updated_at) continue;
        lastUpdatedAt.current[iface.interface_name] = iface.updated_at;
        const existing = next[iface.interface_name] ?? [];
        const point: Point = {
          time: new Date(iface.updated_at).toLocaleTimeString(),
          rx: iface.rx_bps,
          tx: iface.tx_bps,
        };
        const updated = [...existing, point];
        next[iface.interface_name] = updated.length > MAX_POINTS ? updated.slice(updated.length - MAX_POINTS) : updated;
      }
      return next;
    });
  }, [interfaces]);

  const points = history[selected] ?? [];

  return (
    <Card variant="outlined">
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="subtitle1" fontWeight={700}>
            Interface Traffic (live)
          </Typography>
          <TextField select size="small" value={selected} onChange={(e) => setSelected(e.target.value)}>
            {interfaces.map((iface) => (
              <MenuItem key={iface.id} value={iface.interface_name}>
                {iface.interface_name}
              </MenuItem>
            ))}
          </TextField>
        </Stack>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={points}>
            <XAxis dataKey="time" tick={{ fontSize: 11 }} minTickGap={30} />
            <YAxis tickFormatter={(v) => formatBps(v)} tick={{ fontSize: 11 }} width={80} />
            <Tooltip formatter={(v: number) => formatBps(v)} />
            <Line type="monotone" dataKey="rx" name="RX" stroke="#1565c0" dot={false} />
            <Line type="monotone" dataKey="tx" name="TX" stroke="#00897b" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
