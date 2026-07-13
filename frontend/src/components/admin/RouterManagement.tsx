import AddIcon from "@mui/icons-material/Add";
import EditIcon from "@mui/icons-material/Edit";
import {
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
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
import type { RouterCreatePayload, RouterItem, RouterUpdatePayload } from "@/types/router";

const EMPTY: RouterCreatePayload = {
  name: "",
  ip_address: "",
  username: "admin",
  password: "",
  api_port: 8728,
  ssh_port: 22,
  use_ssl: false,
  site: "",
  isp_gateway: "",
  wireguard_endpoint: "",
  wireguard_pool_name: "",
};

function toUpdatePayload(r: RouterItem): RouterUpdatePayload {
  return {
    name: r.name,
    ip_address: r.ip_address,
    username: r.username,
    api_port: r.api_port,
    ssh_port: r.ssh_port,
    site: r.site ?? "",
    isp_gateway: r.isp_gateway ?? "",
    wireguard_endpoint: r.wireguard_endpoint ?? "",
    wireguard_pool_name: r.wireguard_pool_name ?? "",
  };
}

export function RouterManagement() {
  const { data: routers } = useRouters();
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<RouterCreatePayload>(EMPTY);
  const [editingRouter, setEditingRouter] = useState<RouterItem | null>(null);
  const [editForm, setEditForm] = useState<RouterUpdatePayload>({});
  const [testResult, setTestResult] = useState<string | null>(null);

  const createMutation = useMutation({
    mutationFn: (payload: RouterCreatePayload) => routerApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["routers"] });
      setOpen(false);
      setForm(EMPTY);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: RouterUpdatePayload }) => routerApi.update(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["routers"] });
      setEditingRouter(null);
    },
  });

  const testMutation = useMutation({
    mutationFn: (id: number) => routerApi.testConnection(id),
    onSuccess: (result) => setTestResult(result.success ? `OK — RouterOS ${result.routeros_version}` : result.message),
  });

  const field =
    (key: keyof RouterCreatePayload) => (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value }));

  const editField =
    (key: keyof RouterUpdatePayload) => (e: React.ChangeEvent<HTMLInputElement>) =>
      setEditForm((prev) => ({ ...prev, [key]: e.target.value }));

  const openEdit = (r: RouterItem) => {
    setEditingRouter(r);
    setEditForm(toUpdatePayload(r));
  };

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
              <TableCell>VPN Pool</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
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
                <TableCell>{r.wireguard_pool_name ?? "—"}</TableCell>
                <TableCell>
                  <Chip size="small" label={r.is_active ? "active" : "inactive"} color={r.is_active ? "success" : "default"} />
                </TableCell>
                <TableCell align="right">
                  <Button size="small" onClick={() => testMutation.mutate(r.id)}>
                    Test
                  </Button>
                  <IconButton size="small" onClick={() => openEdit(r)}>
                    <EditIcon fontSize="small" />
                  </IconButton>
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
            <TextField
              label="SSH Port"
              type="number"
              helperText="Untuk ambil file backup & sertifikat OpenVPN dari router"
              value={form.ssh_port}
              onChange={field("ssh_port")}
            />
            <TextField label="Site" value={form.site} onChange={field("site")} />
            <TextField label="ISP Gateway" value={form.isp_gateway} onChange={field("isp_gateway")} />
            <TextField
              label="WireGuard Endpoint (host:port)"
              value={form.wireguard_endpoint}
              onChange={field("wireguard_endpoint")}
            />
            <TextField
              label="WireGuard IP Pool Name"
              helperText="Nama /ip pool di router yang dipakai untuk auto-assign IP peer VPN (mis. 'vpn-pool')"
              value={form.wireguard_pool_name}
              onChange={field("wireguard_pool_name")}
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

      <Dialog open={editingRouter !== null} onClose={() => setEditingRouter(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Router — {editingRouter?.name}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField label="Name" value={editForm.name ?? ""} onChange={editField("name")} />
            <TextField label="IP Address" value={editForm.ip_address ?? ""} onChange={editField("ip_address")} />
            <TextField label="Username" value={editForm.username ?? ""} onChange={editField("username")} />
            <TextField
              label="Password (kosongkan jika tidak berubah)"
              type="password"
              value={editForm.password ?? ""}
              onChange={editField("password")}
            />
            <TextField label="API Port" type="number" value={editForm.api_port ?? ""} onChange={editField("api_port")} />
            <TextField label="SSH Port" type="number" value={editForm.ssh_port ?? ""} onChange={editField("ssh_port")} />
            <TextField label="Site" value={editForm.site ?? ""} onChange={editField("site")} />
            <TextField label="ISP Gateway" value={editForm.isp_gateway ?? ""} onChange={editField("isp_gateway")} />
            <TextField
              label="WireGuard Endpoint (host:port)"
              value={editForm.wireguard_endpoint ?? ""}
              onChange={editField("wireguard_endpoint")}
            />
            <TextField
              label="WireGuard IP Pool Name"
              helperText="Nama /ip pool di router yang dipakai untuk auto-assign IP peer VPN (mis. 'vpn-pool')"
              value={editForm.wireguard_pool_name ?? ""}
              onChange={editField("wireguard_pool_name")}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditingRouter(null)}>Cancel</Button>
          <Button
            variant="contained"
            disabled={updateMutation.isPending}
            onClick={() => editingRouter && updateMutation.mutate({ id: editingRouter.id, payload: editForm })}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
}
