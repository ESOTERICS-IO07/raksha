import { TransactionAnalysisResponse } from "@/types";
import { scenarios, transactions } from "./mock-data";
import { mockRiskScenarios } from "@/lib/mockRiskData";
const pause=(ms=500)=>new Promise(r=>setTimeout(r,ms));
export async function getTransactions(){await pause();return transactions;}
export async function analyzeTransaction(input:{recipient:string;amount:number;reason:string;user_id?:string}):Promise<TransactionAnalysisResponse>{
  const res = await fetch("http://127.0.0.1:8000/api/v1/transactions/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: input.user_id || "U001",
      recipient_id: input.recipient === "Rahul Sharma" ? "R020" : "R001",
      amount: input.amount,
      currency: "INR",
      reason: input.reason
    })
  });
  if (!res.ok) {
    throw new Error("Failed to analyze transaction");
  }
  const data = await res.json();
  return {
    ...data,
    recipient_name: input.recipient,
    amount: input.amount,
    reason: input.reason
  };
}
