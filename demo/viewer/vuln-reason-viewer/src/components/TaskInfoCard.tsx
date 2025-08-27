// components/TaskInfoCard.tsx
import React from "react";
import { Task, Metrics } from "@/lib/types";
import { CopyButton } from "./CopyButton";

interface TaskInfoCardProps {
  model: string;
  task: Task;
  metrics: Metrics;
}

const TaskInfoCard: React.FC<TaskInfoCardProps> = ({
  model,
  task,
  metrics,
}) => {
  const formatPercentage = (value: number) => {
    return (value * 100).toFixed(2) + "%";
  };

  const tpPercentage = formatPercentage(metrics.tp / metrics.total);
  const tnPercentage = formatPercentage(metrics.tn / metrics.total);
  const fpPercentage = formatPercentage(metrics.fp / metrics.total);
  const fnPercentage = formatPercentage(metrics.fn / metrics.total);
  const invalidPercentage = formatPercentage(metrics.invalid / metrics.total);
  return (
    <div className="bg-white shadow-md rounded-lg p-4 mb-6">
      <div className="flex justify-between items-start">
        <h2 className="text-xl font-semibold mb-4">Model & Task Information</h2>
        <CopyButton
          text={JSON.stringify({ model, task, metrics }, null, 2)}
          label="Copy JSON"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <p className="text-sm font-medium text-gray-500">Model</p>
          <p className="text-lg">{model}</p>
        </div>

        <div>
          <p className="text-sm font-medium text-gray-500">Dataset</p>
          <p className="text-lg">{task.dataset}</p>
        </div>

        <div>
          <p className="text-sm font-medium text-gray-500">Language</p>
          <p className="text-lg">{task.language}</p>
        </div>

        <div>
          <p className="text-sm font-medium text-gray-500">Prompt Type</p>
          <p className="text-lg">{task.prompt_type}</p>
        </div>

        <div>
          <p className="text-sm font-medium text-gray-500">Add Policy</p>
          <p className="text-lg">{task.add_policy ? "Yes" : "No"}</p>
        </div>

        <div>
          <p className="text-sm font-medium text-gray-500">Metrics</p>
          <p className="text-md">
            TP: {metrics.tp} ({tpPercentage}), TN: {metrics.tn} ({tnPercentage}
            ), FP: {metrics.fp} ({fpPercentage}), FN: {metrics.fn} (
            {fnPercentage}), Invalid: {metrics.invalid} ({invalidPercentage})
          </p>
          <p className="text-lg">Total: {metrics.total}</p>
        </div>
      </div>
    </div>
  );
};

export default TaskInfoCard;
