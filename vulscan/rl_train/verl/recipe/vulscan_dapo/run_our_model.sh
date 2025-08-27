#!/usr/bin/env bash
set -xeuo pipefail

# Ray
RAY_ADDRESS=${RAY_ADDRESS:-"http://localhost:8265"}
WORKING_DIR=${WORKING_DIR:-"${PWD}"}
RUNTIME_ENV=${RUNTIME_ENV:-"${WORKING_DIR}/verl/trainer/runtime_env.yaml"}


ray job submit --no-wait --runtime-env="${RUNTIME_ENV}" \
    --working-dir "${WORKING_DIR}" \
    -- python3 -m recipe.dapo.main_dapo actor_rollout_ref.model.path=secmlr/final_model trainer.experiment_name=dapo_final_model7B_binary_reward trainer.logger=['console','wandb'] trainer.n_gpus_per_node=6 actor_rollout_ref.rollout.n=6
