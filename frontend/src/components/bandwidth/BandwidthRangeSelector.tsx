import { ToggleButton, ToggleButtonGroup } from "@mui/material";
import type { BandwidthRange } from "@/types/traffic";

const OPTIONS: { value: BandwidthRange; label: string }[] = [
  { value: "day", label: "Per Hari" },
  { value: "week", label: "Per Minggu" },
  { value: "month", label: "Per Bulan" },
];

export function BandwidthRangeSelector({
  value,
  onChange,
}: {
  value: BandwidthRange;
  onChange: (range: BandwidthRange) => void;
}) {
  return (
    <ToggleButtonGroup
      size="small"
      exclusive
      value={value}
      onChange={(_, next) => next && onChange(next)}
    >
      {OPTIONS.map((opt) => (
        <ToggleButton key={opt.value} value={opt.value}>
          {opt.label}
        </ToggleButton>
      ))}
    </ToggleButtonGroup>
  );
}
