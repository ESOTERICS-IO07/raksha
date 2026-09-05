export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type FrictionAction = "ALLOW" | "VERIFY" | "STRONG_VERIFY" | "HOLD";
export interface RiskResult { risk_score:number; risk_level:RiskLevel; signals:string[]; action:FrictionAction; message:string; }
export interface TransactionRequest { customer_id:string; recipient_id:string; amount:number; reason:string; description:string; }
export interface SignalResult { score: number; signals: string[] }
export interface TransactionAnalysisResponse { transaction_id:string; recipient_name:string; amount:number; reason:string; timestamp:string; behavior:SignalResult; recipient:SignalResult; intent:SignalResult & { category:string }; risk:{score:number;level:RiskLevel}; friction:{action:FrictionAction;title:string;message:string} }
export interface Transaction extends TransactionAnalysisResponse { status:"ALLOWED"|"VERIFIED"|"HELD"; customer?:string }
export interface Scenario { id:string; name:string; title:string; amount:number; recipient:string; reason:string; expected:string; description:string; analysis:TransactionAnalysisResponse }
export interface DashboardSummary { analyzed:number; verified:number; paused:number; checks:number }
