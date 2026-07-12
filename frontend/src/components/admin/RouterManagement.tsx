import AddIcon from "@mui/icons-material/Add";
import {
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useRouters } from "@/hooks/useRouters";
import { routerApi } from "@/services/routerApi";
import type { RouterCreatePayload } from "@/types/router";

const EMPTY: RouterCreatePayload = {
  name: "",
  ip_address: "",
  username: "admin",
  password: "",
  api_port: 8728,
  use_ssl: false,
  site: "",
  isp_gateway: "",
  wireguard_endpoint: "",
};

export function RouterManagement() {
  const { data: routers } = useRouters();
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<RouterCreatePayload>(EMPTY);
  const [testResult, setTestResult] = useState<string | null>(null);

  const createMutation = useMutation({
    mutationFn: (payload: RouterCreatePayload) => routerApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["routers"] });
      setOpen(false);
      setForm(EMPTY);
    },
  });

  const testMutation = useMutation({
    mutationFn: (id: number) => routerApi.testConnection(id),
    onSuccess: (result) => setTestResult(result.success ? `OK — RouterOS ${result.routeros_version}` : result.message),
  });

  const field =
    (key: keyof RouterCreatePayload) => (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value }));

  return (
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="h6">Routers</Typography>
        <Button startIcon={<AddIcon />} variant="contained" onClick={() => setOpen(true)}>
          Add Router
        </Button>
      </Stack>

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>IP Address</TableCell>
              <TableCell>Site</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Test</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(routers ?? []).map((r) => (
              <TableRow key={r.id} hover>
                <TableCell>{r.name}</TableCell>
                <TableCell>
                  {r.ip_address}:{r.api_port}
                </TableCell>
                <TableCell>{r.site ?? "—"}</TableCell>
                <TableCell>
                  <Chip size="small" label={r.is_active ? "active" : "inactive"} color={r.is_active ? "success" : "default"} />
                </TableCell>
                <TableCell align="right">
                  <Button size="small" onClick={() => testMutation.mutate(r.id)}>
                    Test
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      {testResult && (
        <Typography variant="body2" color="text.secondary">
          {testResult}
        </Typography>
      )}

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Router</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField label="Name" required value={form.name} onChange={field("name")} />
            <TextField label="IP Address" required value={form.ip_address} onChange={field("ip_address")} />
            <TextField label="Username" required value={form.username} onChange={field("username")} />
            <TextField label="Password" required type="password" value={form.password} onChange={field("password")} />
            <TextField label="API Port" type="number" value={form.api_port} onChange={field("api_port")} />
            <TextField label="Site" value={form.site} onChange={field("site")} />
            <TextField label="ISP Gateway" value={form.isp_gateway} onChange={field("isp_gateway")} />
            <TextField
              label="WireGuard Endpoint (host:port)"
              value={form.wireguard_endpoint}
              onChange={field("wireguard_endpoint")}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => createMutation.mutate(form)} disabled={createMutation.isPending}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
}
