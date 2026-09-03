import { TransactionAnalysisResponse } from "@/types";
import { scenarios, transactions } from "./mock-data";
import { mockRiskScenarios } from "@/lib/mockRiskData";
const pause=(ms=500)=>new Promise(r=>setTimeout(r,ms));
export async function getTransactions(){await pause();return transactions;}
export async function analyzeTransaction(input:{recipient:string;amount:number;reason:string}):Promise<TransactionAnalysisResponse>{await pause(900);const text=input.reason.toLowerCase();const state=text.includes("blocked")||text.includes("bank officer")||input.recipient==="Rahul Sharma"?"CRITICAL":input.amount>=20000?"HIGH":input.amount>=5000?"MEDIUM":"LOW";const response=mockRiskScenarios[state];return {...response,recipient_name:input.recipient||response.recipient_name,amount:input.amount||response.amount,reason:input.reason||response.reason};}
