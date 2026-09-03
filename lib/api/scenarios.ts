import { scenarios } from "./mock-data";
import { mockRiskScenarios } from "@/lib/mockRiskData";
const wait=()=>new Promise(r=>setTimeout(r,450));
export async function getScenarios(){await wait();return scenarios;}
export async function runScenario(id:string){await wait(700);const state=id==="normal"?"LOW":id==="unusual"?"HIGH":id==="social"||id==="network"?"CRITICAL":"MEDIUM";return mockRiskScenarios[state];}
