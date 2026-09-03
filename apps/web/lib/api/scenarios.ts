import { Scenario } from "@/types";
export async function getScenarios(): Promise<Scenario[]> {
  const res = await fetch("http://127.0.0.1:8000/api/v1/scenarios");
  if (!res.ok) throw new Error("Failed to fetch scenarios");
  return res.json();
}
export async function runScenario(id: string) {
  const res = await fetch(`http://127.0.0.1:8000/api/v1/scenarios/${id}/run`, {
    method: "POST"
  });
  if (!res.ok) throw new Error("Failed to run scenario");
  return res.json();
}
