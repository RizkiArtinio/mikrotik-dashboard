import { Alert, Button, Stack, TextField } from "@mui/material";
import { useState } from "react";
import { useCreateL2tpPeer } from "@/hooks/useVpnPeers";
import type { L2tpPeerCreatePayload, L2tpPeerResult } from "@/types/vpn";

const EMPTY_FORM: L2tpPeerCreatePayload = {
  username: "",
  password: "",
  description: "",
};

export function L2tpGeneratorForm({
  routerId,
  onGenerated,
}: {
  routerId: number;
  onGenerated: (result: L2tpPeerResult) => void;
}) {
  const [form, setForm] = useState<L2tpPeerCreatePayload>(EMPTY_FORM);
  const mutation = useCreateL2tpPeer(routerId);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(form, { onSuccess: onGenerated });
  };

  const field =
    (key: keyof L2tpPeerCreatePayload) => (e: React.ChangeEvent<HTMLInputElement>) =>
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
            "Failed to generate L2TP account"}
        </Alert>
      )}

      <Button type="submit" variant="contained" disabled={mutation.isPending}>
        {mutation.isPending ? "Generating..." : "Generate"}
      </Button>
    </Stack>
  );
}
