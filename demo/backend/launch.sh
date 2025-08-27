#!/bin/bash

# Script: Run multiple services concurrently
# Usage: ./run_services.sh
export LANGFUSE_PUBLIC_KEY=pk-lf-5d45f1ca-3c12-4fb1-a78d-3343cb588e04
export LANGFUSE_SECRET_KEY=sk-lf-3d96a153-4d2f-40a3-913c-b6f702c4fa43
export LANGFUSE_HOST=https://us.cloud.langfuse.com
# Set color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

source "$(conda info --base)"/etc/profile.d/conda.sh
export PYTHONPATH="$(pwd)/../.."

echo -e "${GREEN}Starting multiple services...${NC}"

# Create logs directory
mkdir -p logs

# Function: cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}Stopping all services...${NC}"
    # Kill all background processes
    jobs -p | xargs -r kill
    echo -e "${RED}All services stopped${NC}"
    exit 0
}

# Trap interrupt signals
trap cleanup SIGINT SIGTERM

echo -e "${BLUE}Starting LiteLLM service (port 35560)...${NC}"
conda activate llm
litellm --port 35560 --config config.yaml > logs/litellm.log 2>&1 &
LITELLM_PID=$!

echo -e "${BLUE}Starting SGLang service (port 25002)...${NC}"
conda activate sglang
CUDA_VISIBLE_DEVICES=0 python -m sglang.launch_server \
    --model-path secmlr/final_model \
    --dtype=bfloat16 \
    --tp 1 \
    --port 25002 \
    --api-key virtueai7355608 \
    --random-seed 42 \
    --enable-torch-compile > logs/sglang.log 2>&1 &
SGLANG_PID=$!

echo -e "${BLUE}Starting API service...${NC}"
conda activate llm
python api.py > logs/api.log 2>&1 &
API_PID=$!

echo -e "${GREEN}All services started successfully!${NC}"
echo -e "Process IDs:"
echo -e "  LiteLLM: ${LITELLM_PID}"
echo -e "  SGLang: ${SGLANG_PID}"
echo -e "  API: ${API_PID}"
echo ""
echo -e "${YELLOW}Log file locations:${NC}"
echo -e "  LiteLLM: logs/litellm.log"
echo -e "  SGLang: logs/sglang.log"
echo -e "  API: logs/api.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for all background processes
wait