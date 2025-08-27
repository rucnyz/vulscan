import datetime
import json
from pathlib import Path
from time import sleep
from typing import Dict, Any, Optional

import openai
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from vulscan.test.test_utils.generation_utils import extract_answer
from vulscan.utils.get_cwe_info import get_cwe_info
from vulscan.utils.sys_prompts import policy, reasoning_user_prompt


# Create logs directory if it doesn't exist
def ensure_log_dir():
    log_dir = Path("logs/data")
    log_dir.mkdir(exist_ok=True)
    return log_dir


# Log request and response to a JSON file
async def log_to_json(endpoint: str, request_data: dict, response_data: dict):
    log_dir = ensure_log_dir()

    # Create a timestamped filename for today
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"{endpoint}_{today}.jsonl"

    # Create log entry with timestamp
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "request": request_data,
        "response": response_data,
    }

    # Append to log file - no need to read the entire file
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Error logging to {log_file}: {str(e)}")


class VulnerabilityStatus:
    Vulnerable = "yes"
    Benign = "no"


class ModelConfig:
    def __init__(
        self,
        model_name: str,
        api_key: str,
        base_url: str = "http://0.0.0.0:25001/v1",
    ):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.client = openai.AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)
        if "QwQ" or "deepseek" in model_name:
            self.reasoning = "You should STRICTLY structure your response as follows:"
        else:
            self.reasoning = "Please think step by step, and output the steps, finally you should STRICTLY structure your response as follows:"

    async def query(
        self, prompt: str, temperature: float = 0, max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Query the model with a given prompt.
        """
        try:
            input_policy = policy
            for cwe_id in ["CWE-125", "CWE-190", "CWE-95"]:
                cwe_number = int(cwe_id.split("-")[-1])
                input_policy += f"\n- {cwe_id}: {get_cwe_info(cwe_number)}"
                assert "Unknown CWE" not in policy, f"Unknown CWE: {cwe_id} is detected"
            input_prompt = reasoning_user_prompt.format(
                CODE=prompt,
                CWE_INFO=input_policy,
                REASONING=self.reasoning,
                ADDITIONAL_CONSTRAINT="",
            )

            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": input_prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                seed=42,
            )
            return {"status": "success", "result": response}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Initialize FastAPI app
app = FastAPI(title="Code Model API", description="API for code analysis model")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Extract(BaseModel):
    code: str
    round: int


# Define request model
class CodeRequest(BaseModel):
    code: str


class ResultResponse(BaseModel):
    status: str
    model: str
    response: str
    cweType: str
    usage: Optional[Dict[str, Any]] = None


class ResultExtractionResponse(BaseModel):
    dependencies: list[str]
    done: bool


# Define response model
class ModelResponse(BaseModel):
    status: str
    result: ResultResponse


class ExtractModelResponse(BaseModel):
    status: str
    result: ResultExtractionResponse


# Preprocessing function
async def preprocess_code(code: str) -> tuple[bool, str]:
    """
    Preprocess the code before sending to model.
    """
    # TODO: 在这里实现代码预处理逻辑

    # 返回预处理后的代码
    return True, code


async def call_model_extraction(code: str, rounds: int) -> Dict[str, Any]:
    """
    使用配置好的模型处理代码
    """
    done = False
    answer = []

    try:
        answer = []
        done = True
        model_result = {
            "dependencies": answer,
            "done": done,
        }
        # response = model_config.query(code)
        #
        # if response["status"] == "error":
        #     return response
        #
        # # 处理模型返回的结果
        # pred = response["result"].choices[0].message.content
        # pred_score, pred_type = extract_answer(pred)
        # model_result = {
        #     "response": pred,
        #     "usage": response["result"].usage.dict()
        #     if hasattr(response["result"].usage, "dict")
        #     else vars(response["result"].usage),
        #     "model": response["result"].model,
        #     "status": pred_score,
        #     "cweType": pred_type,
        # }

        return {"status": "success", "result": model_result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# 使用ModelConfig处理模型调用
async def call_model(code: str) -> Dict[str, Any]:
    """
    使用配置好的模型处理代码
    """
    try:
        response = await model_config.query(code)

        if response["status"] == "error":
            return response

        # 处理模型返回的结果
        pred = response["result"].choices[0].message.content
        pred_score, pred_type = extract_answer(pred)
        model_result = {
            "response": pred,
            "usage": response["result"].usage.dict()
            if hasattr(response["result"].usage, "dict")
            else vars(response["result"].usage),
            "model": response["result"].model,
            "status": pred_score,
            "cweType": pred_type,
        }

        return {"status": "success", "result": model_result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Main API endpoint
@app.post("/analyze", response_model=ModelResponse)
async def analyze_code(request: CodeRequest):
    """
    Analyze code using the model.
    """
    try:
        # Preprocess the code
        status, preprocessed_code = await preprocess_code(request.code)
        if status:
            # Call the model
            result = await call_model(preprocessed_code)
        else:
            raise HTTPException(status_code=400, detail="Code preprocessing failed")
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        response = ModelResponse(result=result["result"], status="success")

        # Log the request and response
        await log_to_json("analyze", request.model_dump(), response.model_dump())

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract", response_model=ExtractModelResponse)
async def extract_code(request: Extract):
    """
    Analyze code using the model.
    """
    try:
        # Preprocess the code
        status, preprocessed_code = await preprocess_code(request.code)
        if status:
            # Call the model
            result = await call_model_extraction(preprocessed_code, request.round)
        else:
            raise HTTPException(status_code=400, detail="Code preprocessing failed")
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        response = ExtractModelResponse(result=result["result"], status="success")

        # Log the request and response
        await log_to_json("extract", request.model_dump(), response.model_dump())

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/suggest", response_model=ExtractModelResponse)
async def suggest(request: Extract):
    """
    Analyze code using the model.
    """
    try:
        # Preprocess the code
        status, preprocessed_code = await preprocess_code(request.code)
        if status:
            # Call the model
            result = await call_model_extraction(preprocessed_code, request.round)
        else:
            raise HTTPException(status_code=400, detail="Code preprocessing failed")
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        response = ExtractModelResponse(result=result["result"], status="success")

        # Log the request and response
        await log_to_json("suggest", request.model_dump(), response.model_dump())

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}


# 初始化模型配置
model_config = ModelConfig(
    # model_name="Qwen/Qwen2.5-7B-Instruct",
    # model_name="Qwen/QwQ-32B",
    # model_name="secmlr/ruizhe_simplier_reasoning_DS-QwQ-Qwen2.5-7B-Instruct_full_sft_full_sft_simplier_reasoning_dsr1",
    # model_name="claude-3-7-sonnet-20250219",
    model_name="secmlr/final_model",
    api_key="empty",
    base_url="http://0.0.0.0:35560/v1",
)
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=4409, reload=True)
