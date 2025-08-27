## backend


```shell
CUDA_VISIBLE_DEVICES=2,3 vllm serve secmlr/final_model --dtype=bfloat16 --tensor-parallel-size=2 --api-key empty --port 25002 --enable-prefix-caching --max-tokens 2048 --seed 42

CUDA_VISIBLE_DEVICES=0 python -m sglang.launch_server --model-path secmlr/final_model --dtype=bfloat16 --tp 1 --port 25002 --api-key virtueai7355608 --random-seed 42 --enable-torch-compile

python -m sglang.launch_server --model secmlr/DS-Noisy_DS-Clean_QWQ-Noisy_QWQ-Clean_Qwen2.5-7B-Instruct_full_sft_1e-5 --dtype=bfloat16 --tp 2 --port 25002 --api-key empty --random-seed 42 --mem-fraction 0.75 --enable-torch-compile \
--speculative-algorithm EAGLE \
--speculative-draft-model-path leptonai/EAGLE-Qwen2.5-7B-Instruct \
--speculative-num-steps 5 \
--speculative-num-draft-tokens 8 \
--speculative-eagle-topk 4

python backend/api.py

litellm --port 35560 --config config.yaml
```
## Viewer
Convert results:
```shell
python demo/convert_old_input.py \
  --result_dir results/train \
  --out_dir demo/viewer/vuln-reason-viewer/data \
  --pairs demo/data/primevul_pairs.pkl demo/data/sven_pairs.pkl

```


Build next:
```bash
# Navigate to your Next.js app directory
cd demo/viewer/vuln-reason-viewer

# Install dependencies
npm install

# Run in development mode
npm run dev

# Build for production
npm run build

# Test production build locally
npm start
```


File management apis:
```bash
## Upload a File
curl -X POST http://localhost:3001/api/files/upload \
  -F 'file=@/path/to/your/file.txt'

## List Files
curl -X GET http://localhost:3001/api/files/list

## Delete a File
curl -X DELETE "http://localhost:3001/api/files/delete?filename=file.txt"
```
