import { Alert, Button, Stack, TextField } from "@mui/material";
import { useState } from "react";
import { useCreateOvpnPeer } from "@/hooks/useVpnPeers";
import type { OvpnPeerCreatePayload, OvpnPeerResult } from "@/types/vpn";

const EMPTY_FORM: OvpnPeerCreatePayload = {
  username: "",
  password: "",
  description: "",
};

export function OvpnGeneratorForm({
  routerId,
  onGenerated,
}: {
  routerId: number;
  onGenerated: (result: OvpnPeerResult) => void;
}) {
  const [form, setForm] = useState<OvpnPeerCreatePayload>(EMPTY_FORM);
  const mutation = useCreateOvpnPeer(routerId);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(form, { onSuccess: onGenerated });
  };

  const field =
    (key: keyof OvpnPeerCreatePayload) => (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value }));

  return (
    <Stack component="form" onSubmit={handleSubmit} spacing={2} maxWidth={480}>
      <TextField
        label="Username (opsional)"
        placeholder="Kosongkan untuk auto-generate"
        helperText="Kalau kosong, username dibuat otomatis (mis. vpn-a1b2c3)."
        value={form.username}
        onChange={field("username")}
      />
      <TextField
        label="Password (opsional)"
        placeholder="Kosongkan untuk auto-generate"
        value={form.password}
        onChange={field("password")}
      />
      <TextField label="Description" value={form.description} onChange={field("description")} multiline rows={2} />

      {mutation.isError && (
        <Alert severity="error">
          {(mutation.error as Error & { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
            "Failed to generate OpenVPN account"}
        </Alert>
      )}

      <Button type="submit" variant="contained" disabled={mutation.isPending}>
        {mutation.isPending ? "Generating..." : "Generate"}
      </Button>
    </Stack>
  );
}
