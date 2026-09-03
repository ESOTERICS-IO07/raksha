import { DashboardSummary } from "@/types";
const wait=()=>new Promise(r=>setTimeout(r,350));
export async function getDashboardSummary():Promise<DashboardSummary>{await wait();return {analyzed:128,verified:18,paused:4,checks:382};}
export async function getBankMetrics(){await wait();return {analyzed:1248,allowed:1103,verified:94,held:31,highRisk:42,critical:11};}
