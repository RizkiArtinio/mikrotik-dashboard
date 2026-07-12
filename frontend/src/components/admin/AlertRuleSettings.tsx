import {
  Paper,
  Stack,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { alertApi } from "@/services/alertApi";
import type { AlertRuleUpdatePayload } from "@/types/alert";

export function AlertRuleSettings() {
  const { data: rules } = useQuery({ queryKey: ["alert-rules"], queryFn: alertApi.listRules });
  const queryClient = useQueryClient();

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: AlertRuleUpdatePayload }) => alertApi.updateRule(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alert-rules"] }),
  });

  return (
    <Stack spacing={2}>
      <Typography variant="h6">Alert Rules</Typography>
      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Alert Type</TableCell>
              <TableCell>Threshold</TableCell>
              <TableCell>Cooldown (min)</TableCell>
              <TableCell align="center">Telegram</TableCell>
              <TableCell align="center">Email</TableCell>
              <TableCell align="center">Enabled</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(rules ?? []).map((rule) => (
              <TableRow key={rule.id} hover>
                <TableCell>{rule.alert_type.replace("_", " ")}</TableCell>
                <TableCell>
                  {rule.threshold_value != null ? (
                    <TextField
                      size="small"
                      type="number"
                      defaultValue={rule.threshold_value}
                      onBlur={(e) =>
                        updateMutation.mutate({ id: rule.id, payload: { threshold_value: Number(e.target.value) } })
                      }
                      sx={{ width: 90 }}
                    />
                  ) : (
                    "—"
                  )}
                </TableCell>
                <TableCell>
                  <TextField
                    size="small"
                    type="number"
                    defaultValue={rule.cooldown_minutes}
                    onBlur={(e) =>
                      updateMutation.mutate({ id: rule.id, payload: { cooldown_minutes: Number(e.target.value) } })
                    }
                    sx={{ width: 90 }}
                  />
                </TableCell>
                <TableCell align="center">
                  <Switch
                    checked={rule.notify_telegram}
                    onChange={(e) =>
                      updateMutation.mutate({ id: rule.id, payload: { notify_telegram: e.target.checked } })
                    }
                  />
                </TableCell>
                <TableCell align="center">
                  <Switch
                    checked={rule.notify_email}
                    onChange={(e) => updateMutation.mutate({ id: rule.id, payload: { notify_email: e.target.checked } })}
                  />
                </TableCell>
                <TableCell align="center">
                  <Switch
                    checked={rule.is_enabled}
                    onChange={(e) => updateMutation.mutate({ id: rule.id, payload: { is_enabled: e.target.checked } })}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Stack>
  );
}
