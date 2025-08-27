export type VulnType = "none" | string;

export interface ResultSample {
  input: string;
  code: string;
  pair_code: string | null;
  is_vuln: boolean;
  vuln_type: VulnType;
  output: string;
  pred_is_vuln: boolean | null;
  pred_vuln_type: VulnType | null;
  unparsed_pred_vuln_type: string;
  judge: "tp" | "tn" | "fp" | "fn" | "invalid";
  idx: string;
}

export interface ConversationMessage {
  from: "user" | "assistant";
  value: string;
}

export interface ConversationData {
  system?: string;
  idx?: number;
  cwe?: string[];
  conversations: ConversationMessage[];
}

export type PromptType = "cot" | "own_cot" | "none";

export interface Task {
  dataset: string;
  language: string;
  prompt_type: PromptType;
  add_policy: boolean;
}

export interface Metrics {
  total: number;
  tp: number;
  tn: number;
  fp: number;
  fn: number;
  invalid: number;
}

export interface ResultData {
  model: string;
  task: Task;
  metrics: Metrics;
  results: ResultSample[];
}