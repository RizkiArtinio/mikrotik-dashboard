import { Alert, Button, Stack, TextField } from "@mui/material";
import { useState } from "react";
import { useCreateWireguardPeer } from "@/hooks/useVpnPeers";
import type { WireguardPeerCreatePayload, WireguardPeerResult } from "@/types/vpn";

const EMPTY_FORM: WireguardPeerCreatePayload = {
  username: "",
  allowed_ip: "",
  dns: "1.1.1.1",
  endpoint: "",
  description: "",
};

export function VpnGeneratorForm({
  routerId,
  onGenerated,
}: {
  routerId: number;
  onGenerated: (result: WireguardPeerResult) => void;
}) {
  const [form, setForm] = useState<WireguardPeerCreatePayload>(EMPTY_FORM);
  const mutation = useCreateWireguardPeer(routerId);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(form, { onSuccess: onGenerated });
  };

  const field =
    (key: keyof WireguardPeerCreatePayload) => (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value }));

  return (
    <Stack component="form" onSubmit={handleSubmit} spacing={2} maxWidth={480}>
      <TextField label="Nama User" required value={form.username} onChange={field("username")} />
      <TextField
        label="Allowed IP (opsional)"
        placeholder="Kosongkan untuk auto-assign dari VPN pool router"
        helperText="IP akan dipilih otomatis dari pool VPN yang sudah dikonfigurasi di router, kecuali diisi manual."
        value={form.allowed_ip}
        onChange={field("allowed_ip")}
      />
      <TextField label="DNS" required value={form.dns} onChange={field("dns")} />
      <TextField
        label="Endpoint (opsional, override router default)"
        placeholder="vpn.example.com:13231"
        value={form.endpoint}
        onChange={field("endpoint")}
      />
      <TextField label="Description" value={form.description} onChange={field("description")} multiline rows={2} />

      {mutation.isError && (
        <Alert severity="error">
          {(mutation.error as Error & { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
            "Failed to generate WireGuard peer"}
        </Alert>
      )}

      <Button type="submit" variant="contained" disabled={mutation.isPending}>
        {mutation.isPending ? "Generating..." : "Generate"}
      </Button>
    </Stack>
  );
}
