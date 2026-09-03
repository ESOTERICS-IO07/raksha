import { DashboardSummary } from "@/types";
const wait=()=>new Promise(r=>setTimeout(r,350));
export async function getDashboardSummary(): Promise<DashboardSummary> {
  const res = await fetch("http://127.0.0.1:8000/api/v1/dashboard/summary");
  if (!res.ok) throw new Error("Failed to fetch dashboard summary");
  return res.json();
}

export async function getBankMetrics() {
  const res = await fetch("http://127.0.0.1:8000/api/v1/dashboard/summary");
  if (!res.ok) throw new Error("Failed to fetch bank metrics");
  return res.json();
}
