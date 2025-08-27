```shell
cd vulscan/rl_train/verl
export PYTHONPATH=.:~/projects/vulllm
python recipe/vulscan_dapo/src/main_dapo.py actor_rollout_ref.model.path=Qwen/Qwen2.5-7B-Instruct trainer.experiment_name=dapo_qwen7B_binary_reward trainer.logger='['console', 'wandb']' trainer.n_gpus_per_node=4

python recipe/vulscan_dapo/src/main_dapo.py actor_rollout_ref.model.path=secmlr/final_model trainer.experiment_name=dapo_final_model trainer.logger='['console']' trainer.n_gpus_per_node=4
# trainer.n_gpus_per_node=2
# check verl/utils/reward_score/vd.py

# upload
python scripts/model_merger.py merge \
    --backend fsdp \
    --local_dir checkpoints/vulscan/dapo_final_model7B_binary_reward/global_step_10/actor \
    --target_dir checkpoints/vulscan/dapo_final_model7B_binary_reward/global_step_10/hf \
    --hf_upload_path secmlr/dapo_final_model
# profile
py-spy record -o profile.svg -- python recipe/vulscan_dapo/src/main_dapo.py
```