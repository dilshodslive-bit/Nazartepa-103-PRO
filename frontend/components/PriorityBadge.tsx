import type { Priority } from "@/lib/types";
import { priorityLabel } from "@/lib/i18n";

const styles: Record<Priority, string> = {
  red: "bg-red-600 text-white",
  yellow: "bg-amber-500 text-black",
  green: "bg-green-600 text-white",
};

export default function PriorityBadge({ priority }: { priority: Priority | null }) {
  if (!priority) {
    return (
      <span className="rounded-full bg-slate-600 px-2 py-0.5 text-xs text-slate-200">
        —
      </span>
    );
  }
  return (
    <span
      className={`rounded-full px-2 py-0.5 text-xs font-semibold ${styles[priority]}`}
    >
      {priorityLabel[priority]}
    </span>
  );
}
