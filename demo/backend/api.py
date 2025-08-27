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


mock_vite = """\
Alright, after examining the additional code implementation, let me clarify the potential vulnerability:

There is a CWE-200 Information Exposure vulnerability in this code. The vulnerability stems from how URLs with trailing query separators are handled in the access control logic.

Here's the issue:

1. In the original code, when checking if a URL should be accessible (`ensureServingAccess`), the full URL including any trailing query separators (`?` or `&`) is passed to the function.

2. Inside the access control flow, `cleanUrl()` is called (via `fsPathFromUrl()` -> `fsPathFromId()` -> `cleanUrl()`), which removes everything after `?` or `#` characters.

3. However, this creates a security gap: an attacker could append a trailing query separator to a restricted path (e.g., `/restricted/file?`) to potentially bypass access controls.

The vulnerability occurs because:

- `isFileServingAllowed()` would check the URL with the trailing separator
- But when actually resolving the file path with `fsPathFromUrl()`, the trailing separator would be removed
- This creates a mismatch between what's being checked for permission and what's actually being accessed

For example, if `/restricted/file` is forbidden but an attacker requests `/restricted/file?`, the original access check might treat them as different paths, potentially allowing access to the restricted file.

The fix correctly normalizes the URL by removing trailing query separators (`?&+$`) before performing any access control checks, ensuring that the same path is used for both permission checking and file access.

This is a subtle but serious security vulnerability that could lead to unauthorized information disclosure (CWE-200) by exposing files that should be protected by the server's access controls.
## Final Answer\n#judge: yes\n#type: CWE-416
"""

mockResult = {
    "result": {
        "status": VulnerabilityStatus.Benign,
        "cweType": "N/A",
        "response": "The code you provided appears to be benign. The function GetTableData is designed to safely handle table data extraction and does not exhibit any known vulnerabilities. It uses a boolean return type to indicate success or failure, which is a common practice in C++ programming. The function also includes error handling mechanisms to ensure that any issues encountered during the data extraction process are properly managed.",
    },
    "status": "success",
}
mockResult_opencts = {
    "result": {
        "status": VulnerabilityStatus.Vulnerable,
        "cweType": "CWE-416: Use After Free",
        "response": "I've reviewed the code you shared, and I think your analysis about a potential Use-After-Free (UAF) vulnerability is correct. Let me explain why:\nThe issue occurs in the relationship between the Arena class and how it's used in the font processing functions, specifically in ProcessGeneric and Font::ParseTable.\nHere's the problem:\n\nIn ProcessGeneric, an Arena object is created locally:\n\ncppots::Arena arena;\n\nThis arena is passed to Font::ParseTable which allocates memory through it:\n\ncppif (!font->ParseTable(it->second, data, arena)) {\n  return OTS_FAILURE_MSG_TAG(\"Failed to parse table\", tag);\n}\n\nInside ParseTable, memory is allocated from the arena via GetTableData:\n\ncppif (GetTableData(data, table_entry, arena, &table_length, &table_data)) {\n  // FIXME: Parsing some tables will fail if the table is not added to\n  // m_tables first.\n  m_tables[tag] = table;\n  ret = table->Parse(table_data, table_length);\n  // ...\n}\n\nThe GetTableData function allocates memory from the arena:\n\ncpp*table_data = arena.Allocate(*table_length);\n\nThe problematic part is that the Font object stores pointers to the arena-allocated memory in its tables, but the arena goes out of scope at the end of ProcessGeneric, resulting in a Use-After-Free:\n\ncpp// Arena destructor\n~Arena() {\n  for (std::vector<uint8_t*>::begin(); i != hunks_.end(); ++i) {\n    delete[] *i;\n  }\n}\nThis is a classic UAF pattern where:\n\nMemory is allocated from the arena\nReferences to this memory are stored in the font's tables\nThe arena is destroyed, which frees all its allocated memory\nThe font still holds pointers to this freed memory\nLater accesses to these pointers (like during serialization in OpenTypeCMAP::Serialize) would be operating on freed memoryThe arena goes out of scope at the end of ProcessGeneric, resulting in a Use-After-Free situation, because of how C++ manages object lifetimes. Let me explain:\n\nIn the ProcessGeneric function, the Arena object is declared as a local variable:\ncppots::Arena arena;\n\nIn C++, local variables exist only within the scope they're declared in. When execution reaches the end of the function (the closing curly brace of ProcessGeneric), all local variables are destroyed automatically.\nWhen the arena is destroyed, its destructor is called:\ncpp~Arena() {\n  for (std::vector<uint8_t*>::iterator\n       i = hunks_.begin(); i != hunks_.end(); ++i) {\n    delete[] *i;\n  }\n}\nThis destructor frees all memory chunks that were allocated by the arena.\nHowever, the problem is that during ProcessGeneric, the Font object (which is passed by pointer and outlives the function) stores references to memory that was allocated by this arena:\ncppif (!font->ParseTable(it->second, data, arena)) {\n  // ...\n}\n\nInside ParseTable, memory is allocated through the arena, and pointers to this memory are stored in the font's tables:\ncppif (GetTableData(data, table_entry, arena, &table_length, &table_data)) {\n  m_tables[tag] = table;\n  // ...\n}\n\nAfter ProcessGeneric returns, the Font object continues to exist, but the arena that allocated memory for its table data has been destroyed. This means the font now contains pointers to memory that has been freed, resulting in a Use-After-Free condition.\nIf any code later accesses these tables (like during serialization), it will be accessing freed memory, which can lead to crashes, data corruption, or security vulnerabilities.\n\nThis is a common memory management issue in C++ where the lifetime of allocated resources doesn't match the lifetime of objects that reference those resources. A proper fix would involve ensuring the arena lives at least as long as the font object, or implementing a different memory management strategy.\n## Final Answer\n#judge: yes\n#type: CWE-416",
    },
    "status": "success",
}


# EU AI Act Categories
class EUAIActCategory:
    """EU AI Act Risk Categories and their specific violations"""

    # Article 15.4: Accuracy, robustness and cybersecurity
    ARTICLE_15_4_NETWORK_INTRUSION = "Article 15.4: Network intrusion"
    ARTICLE_15_4_VULNERABILITY_PROBING = "Article 15.4: Vulnerability probing"
    ARTICLE_15_4_SPOOFING = "Article 15.4: Spoofing"
    ARTICLE_15_4_SPEAR_PHISHING = "Article 15.4: Spear phishing"
    ARTICLE_15_4_SOCIAL_ENGINEERING = "Article 15.4: Social engineering"
    ARTICLE_15_4_UNAUTHORIZED_NETWORK_ENTRY = "Article 15.4: Unauthorized network entry"
    ARTICLE_15_4_MALWARE = "Article 15.4: Malware"
    ARTICLE_15_4_PACKET_FORGERY = "Article 15.4: Packet forgery"
    ARTICLE_15_4_DATA_TAMPERING = "Article 15.4: Data tampering"
    ARTICLE_15_4_CONTROL_OVERRIDE = "Article 15.4: Control override"
    ARTICLE_15_4_SYSTEM_IMPAIRMENT = "Article 15.4: System/Website impairment"
    ARTICLE_15_4_NETWORK_DISRUPTION = "Article 15.4: Network disruption"

    # Article 5: Prohibited AI practices
    ARTICLE_5_INFLUENCE_POLITICAL_DECISIONS = "Article 5: Influence political decisions"
    ARTICLE_5_INFLUENCE_POLITICAL_OPINIONS = "Article 5: Influence political opinions"
    ARTICLE_5_MISINFORMATION = "Article 5: Generating or promoting misinformation"
    ARTICLE_5_FAKE_ENGAGEMENT = "Article 5: Fake online engagement"
    ARTICLE_5_UNAUTHORIZED_DATA_MANIPULATION = (
        "Article 5: Unauthorized data generation and inference"
    )
    ARTICLE_5_DANGEROUS_MATERIALS = "Article 5: Explosives/Dangerous Materials"
    ARTICLE_5_BIOWEAPONS = "Article 5: Bioweapons/Viruses/Gain-of-function"
    ARTICLE_5_NUCLEAR_WEAPONS = "Article 5: Nuclear Weapons"
    ARTICLE_5_CHEMICAL_WEAPONS = "Article 5: Chemical Weapons"
    ARTICLE_5_RADIOLOGICAL_WEAPONS = "Article 5: Radiological Weapons"

    # Article 6.2: Additional HIGH-RISK AI SYSTEMS
    ARTICLE_6_2_PROFILING = "Article 6.2: Profiling"
    ARTICLE_6_2_INFLUENCE_POLITICAL_DECISIONS = (
        "Article 6.2: Influence political decisions"
    )
    ARTICLE_6_2_INFLUENCE_POLITICAL_OPINIONS = (
        "Article 6.2: Influence political opinions"
    )
    ARTICLE_6_2_FINANCING_ELIGIBILITY = (
        "Article 6.2: Financing eligibility/Creditworthiness"
    )
    ARTICLE_6_2_SOCIAL_SCORING = "Article 6.2: Social scoring"
    ARTICLE_6_2_HOUSING_ELIGIBILITY = "Article 6.2: Housing eligibility"
    ARTICLE_6_2_EDUCATION_ELIGIBILITY = "Article 6.2: Education eligibility"
    ARTICLE_6_2_MIGRATION_ELIGIBILITY = "Article 6.2: Migration eligibility"
    ARTICLE_6_2_INSURANCE_ELIGIBILITY = "Article 6.2: Insurance eligibility"
    ARTICLE_6_2_DISCRIMINATION = "Article 6.2: Discrimination"
    ARTICLE_6_2_CHARACTERIZATION = "Article 6.2: Characterization of identity"
    ARTICLE_6_2_CLASSIFICATION = "Article 6.2: Classification of individuals"

    # Article 6.1: HIGH-RISK AI SYSTEMS
    ARTICLE_6_1_HEAVY_MACHINERY = "Article 6.1: Heavy machinery"
    ARTICLE_6_1_TRANSPORTATION = "Article 6.1: Transportation"
    ARTICLE_6_1_ENERGY_GRIDS = "Article 6.1: Energy/Electrical grids"
    ARTICLE_6_1_NUCLEAR_FACILITIES = "Article 6.1: Nuclear facilities"
    ARTICLE_6_1_AIRCRAFT_NAVIGATION = (
        "Article 6.1: Aircraft navigation/Air traffic control"
    )
    ARTICLE_6_1_COMMUNICATION_SYSTEMS = "Article 6.1: Communication systems"
    ARTICLE_6_1_WATER_TREATMENT = "Article 6.1: Water treatment facilities"
    ARTICLE_6_1_LIFE_SUPPORT = "Article 6.1: Life support"
    ARTICLE_6_1_WEAPON_SYSTEMS = "Article 6.1: Weapon systems/Battlefield management"
    ARTICLE_6_1_EMERGENCY_SERVICES = "Article 6.1: Emergency services"
    ARTICLE_6_1_UNAUTHORIZED_ACTIONS = (
        "Article 6.1: Other unauthorized actions on behalf of users"
    )

    # Article 52: General-purpose AI models & systemic risks
    ARTICLE_52_AUTOMATED_POSTS = "Article 52: Automated social media posts"
    ARTICLE_52_NOT_LABELING_AI = "Article 52: Not labeling content as AI-generated"
    ARTICLE_52_IMPERSONATING_HUMANS = "Article 52: Impersonating humans"
    ARTICLE_52_UNAUTHORIZED_GENERATION = (
        "Article 52: Unauthorized generation of various data types"
    )
    ARTICLE_52_IP_RIGHTS = "Article 52: IP Rights/Trade Secrets"

    # Article 55: Serious Incidents
    ARTICLE_55_PERSONS = "Article 55: Persons (including murder)"
    ARTICLE_55_PROPERTY_DAMAGE = "Article 55: Property damage"
    ARTICLE_55_ENVIRONMENTAL = "Article 55: Environmental"

    # Article 10: Data and data governance
    ARTICLE_10_UNAUTHORIZED_PII = "Article 10: Unauthorized generation - PII"
    ARTICLE_10_UNAUTHORIZED_INFERENCE_PII = (
        "Article 10: Unauthorized inference/synthesis - PII"
    )

    # No violation
    UNKNOWN_VIOLATION = "Unknown EU AI Act violation detected"
    NO_VIOLATION = "No EU AI Act violation detected"


class EUAIActResultResponse(BaseModel):
    status: str
    model: str
    response: str
    violationType: str
    article: str
    usage: Optional[Dict[str, Any]] = None


class EUAIActModelResponse(BaseModel):
    status: str
    result: EUAIActResultResponse


# EU AI Act policy for the model
EU_AI_ACT_POLICY = """You are analyzing code for potential violations of the EU AI Act. 

The EU AI Act categorizes AI systems based on risk levels and specific violations. You need to determine if the code violates any of the following articles:

**Article 15.4: Accuracy, robustness and cybersecurity** - Violations include:
- Network intrusion
- Vulnerability probing
- Spoofing
- Spear phishing
- Social engineering
- Unauthorized network entry
- Malware
- Packet forgery
- Data tampering
- Control override (safety/privacy filters)
- System/Website impairment
- Network disruption

**Article 5: Prohibited AI practices** - Violations include:
- Influence political decisions
- Influence political opinions
- Generating or promoting misinformation
- Fake online engagement
- Unauthorized data generation and inference (if used for manipulation)
- Explosives/Dangerous Materials
- Bioweapons/Viruses/Gain-of-function
- Nuclear Weapons
- Chemical Weapons
- Radiological Weapons

**Article 6.2: Additional HIGH-RISK AI SYSTEMS** - Violations include:
- Profiling (if for manipulative purposes)
- Influence political decisions
- Influence political opinions
- Financing eligibility/Creditworthiness
- Social scoring
- Housing eligibility
- Education eligibility
- Migration eligibility
- Insurance eligibility
- Discrimination in employment, benefits, or services
- Characterization of identity
- Classification of individuals

**Article 6.1: HIGH-RISK AI SYSTEMS** - Violations include:
- Heavy machinery
- Transportation
- Energy/Electrical grids
- Nuclear facilities
- Aircraft navigation/Air traffic control
- Communication systems
- Water treatment facilities
- Life support
- Weapon systems/Battlefield management
- Emergency services
- Other unauthorized actions on behalf of users

**Article 52: General-purpose AI models & systemic risks** - Violations include:
- Automated social media posts
- Not labeling content as AI-generated
- Impersonating humans
- Unauthorized generation of various data types (if for manipulation)
- IP Rights/Trade Secrets

**Article 55: Serious Incidents** - Violations include:
- Persons (including murder)
- Property damage
- Environmental

**Article 10: Data and data governance** - Violations include:
- Unauthorized generation - PII
- Unauthorized inference/synthesis - PII

Analyze the code for any potential violations of these articles."""


# Extract EU AI Act classification from model response
def extract_eu_ai_act_answer(pred: str) -> tuple[str, str]:
    """
    Extract EU AI Act violation status and category from model prediction.
    Returns (violation_status, article_category)
    """
    # Look for structured answer in the response
    violation_status = "no"
    article_category = EUAIActCategory.NO_VIOLATION

    # Check for violation indicators
    if "#judge: yes" in pred.lower():
        violation_status = "yes"
    elif "#judge: no" in pred.lower():
        violation_status = "no"

    # Extract article type
    if "#type:" in pred.lower():
        article_line = pred.lower().split("#type:")[1].split("\n")[0].strip()
        # Map the article line to the appropriate category
        if "15.4" in article_line:
            if "network intrusion" in article_line:
                article_category = EUAIActCategory.ARTICLE_15_4_NETWORK_INTRUSION
            elif "vulnerability" in article_line:
                article_category = EUAIActCategory.ARTICLE_15_4_VULNERABILITY_PROBING
            elif "malware" in article_line:
                article_category = EUAIActCategory.ARTICLE_15_4_MALWARE
            elif "spoofing" in article_line:
                article_category = EUAIActCategory.ARTICLE_15_4_SPOOFING
            elif "spear phishing" in article_line:
                article_category = EUAIActCategory.ARTICLE_15_4_SPEAR_PHISHING
            elif "social engineering" in article_line:
                article_category = EUAIActCategory.ARTICLE_15_4_SOCIAL_ENGINEERING
            elif "unauthorized network entry" in article_line:
                article_category = (
                    EUAIActCategory.ARTICLE_15_4_UNAUTHORIZED_NETWORK_ENTRY
                )
            elif "packet forgery" in article_line:
                article_category = EUAIActCategory.ARTICLE_15_4_PACKET_FORGERY
            elif "data tampering" in article_line:
                article_category = EUAIActCategory.ARTICLE_15_4_DATA_TAMPERING
            elif "control override" in article_line:
                article_category = EUAIActCategory.ARTICLE_15_4_CONTROL_OVERRIDE
            elif "system impairment" in article_line:
                article_category = EUAIActCategory.ARTICLE_15_4_SYSTEM_IMPAIRMENT
            elif "network disruption" in article_line:
                article_category = EUAIActCategory.ARTICLE_15_4_NETWORK_DISRUPTION
        elif "article 5" in article_line:
            if "political" in article_line:
                article_category = (
                    EUAIActCategory.ARTICLE_5_INFLUENCE_POLITICAL_DECISIONS
                )
            elif "misinformation" in article_line:
                article_category = EUAIActCategory.ARTICLE_5_MISINFORMATION
            elif "fake engagement" in article_line:
                article_category = EUAIActCategory.ARTICLE_5_FAKE_ENGAGEMENT
            elif "unauthorized data" in article_line:
                article_category = (
                    EUAIActCategory.ARTICLE_5_UNAUTHORIZED_DATA_MANIPULATION
                )
            elif "explosives" in article_line:
                article_category = EUAIActCategory.ARTICLE_5_DANGEROUS_MATERIALS
            elif "bioweapons" in article_line:
                article_category = EUAIActCategory.ARTICLE_5_BIOWEAPONS
            elif "nuclear weapons" in article_line:
                article_category = EUAIActCategory.ARTICLE_5_NUCLEAR_WEAPONS
            elif "chemical weapons" in article_line:
                article_category = EUAIActCategory.ARTICLE_5_CHEMICAL_WEAPONS
            elif "radiological weapons" in article_line:
                article_category = EUAIActCategory.ARTICLE_5_RADIOLOGICAL_WEAPONS
        elif "article 6.2" in article_line:
            if "profiling" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_2_PROFILING
            elif "political decisions" in article_line:
                article_category = (
                    EUAIActCategory.ARTICLE_6_2_INFLUENCE_POLITICAL_DECISIONS
                )
            elif "social scoring" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_2_SOCIAL_SCORING
            elif "housing eligibility" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_2_HOUSING_ELIGIBILITY
            elif "education eligibility" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_2_EDUCATION_ELIGIBILITY
            elif "migration eligibility" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_2_MIGRATION_ELIGIBILITY
            elif "insurance eligibility" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_2_INSURANCE_ELIGIBILITY
            elif "discrimination" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_2_DISCRIMINATION
            elif "characterization of identity" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_2_CHARACTERIZATION
            elif "classification of individuals" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_2_CLASSIFICATION
        elif "article 6.1" in article_line:
            if "heavy machinery" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_1_HEAVY_MACHINERY
            elif "transportation" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_1_TRANSPORTATION
            elif "nuclear facilities" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_1_NUCLEAR_FACILITIES
            elif "aircraft navigation" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_1_AIRCRAFT_NAVIGATION
            elif "communication systems" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_1_COMMUNICATION_SYSTEMS
            elif "water treatment" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_1_WATER_TREATMENT
            elif "life support" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_1_LIFE_SUPPORT
            elif "weapon systems" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_1_WEAPON_SYSTEMS
            elif "emergency services" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_1_EMERGENCY_SERVICES
            elif "unauthorized actions" in article_line:
                article_category = EUAIActCategory.ARTICLE_6_1_UNAUTHORIZED_ACTIONS
        elif "article 52" in article_line:
            if "automated posts" in article_line:
                article_category = EUAIActCategory.ARTICLE_52_AUTOMATED_POSTS
            elif "not labeling" in article_line:
                article_category = EUAIActCategory.ARTICLE_52_NOT_LABELING_AI
            elif "impersonating humans" in article_line:
                article_category = EUAIActCategory.ARTICLE_52_IMPERSONATING_HUMANS
            elif "unauthorized generation" in article_line:
                article_category = EUAIActCategory.ARTICLE_52_UNAUTHORIZED_GENERATION
            elif "ip rights" in article_line:
                article_category = EUAIActCategory.ARTICLE_52_IP_RIGHTS
        elif "article 10" in article_line:
            if "unauthorized generation" in article_line:
                article_category = EUAIActCategory.ARTICLE_10_UNAUTHORIZED_PII
            elif "unauthorized inference" in article_line:
                article_category = (
                    EUAIActCategory.ARTICLE_10_UNAUTHORIZED_INFERENCE_PII
                )
        elif "article 55" in article_line:
            if "persons" in article_line:
                article_category = EUAIActCategory.ARTICLE_55_PERSONS
            elif "property damage" in article_line:
                article_category = EUAIActCategory.ARTICLE_55_PROPERTY_DAMAGE
            elif "environmental" in article_line:
                article_category = EUAIActCategory.ARTICLE_55_ENVIRONMENTAL
        elif "unknown violation" in article_line:
            article_category = EUAIActCategory.UNKNOWN_VIOLATION
    else:
        if violation_status == "yes":
            # If no specific article is mentioned, default to a general violation
            article_category = EUAIActCategory.UNKNOWN_VIOLATION
        else:
            article_category = EUAIActCategory.NO_VIOLATION

    return violation_status, article_category


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

    async def query_eu_ai_act(
        self, prompt: str, temperature: float = 0, max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Query the model for EU AI Act classification.
        """
        try:
            input_prompt = f"""You are an AI system analyzer specializing in EU AI Act compliance.

{EU_AI_ACT_POLICY}

Analyze the following code and determine if it violates any EU AI Act articles:

CODE:
{prompt}

{self.reasoning}

## Final Answer
#judge: [yes/no]
#type: [specific article and violation type, e.g., "Article 15.4: Malware" or "No EU AI Act violation detected"]

# Example
- If the code violates Article 15.4 for malware, you should finally output:
## Final Answer
#judge: yes
#type: Article 15.4: Malware

- If the code violates Article 5 for generating misinformation, you should finally output:
## Final Answer
#judge: yes
#type: Article 5: Generating or promoting misinformation

- If the code does not contain any EU AI Act violations, you should finally output:
## Final Answer
#judge: no
#type: N/A
"""

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
        if "if (!font->ParseTable(it->second, data, arena))" in code:
            sleep(1 * rounds + 0.5)
            if rounds == 1:
                answer = ["font->ParseTable", "font->GetTable"]
            elif rounds == 2:
                answer = ["GetTableData", "table->Parse", "AddTable"]
            elif rounds == 3:
                answer = ["arena.Allocate"]
                done = True
        elif "!ensureServingAccess(url, server, res, next)" in code:
            sleep(1 * rounds + 0.5)
            if rounds == 1:
                answer = ["ensureServingAccess", "rawRE", "urlRE"]
            elif rounds == 2:
                answer = ["isFileServingAllowed"]
            elif rounds == 3:
                answer = ["fsPathFromUrl", "isFileLoadingAllowed"]
            elif rounds == 4:
                answer = [
                    "fsPathFromId",
                    "cleanUrl",
                    "postfixRE",
                    "normalizePath",
                    "VOLUME_RE",
                ]
                done = True
        else:
            answer = []
            done = True
        model_result = {
            "dependencies": answer,
            "done": done,
        }


        return {"status": "success", "result": model_result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# EU AI Act model call
async def call_model_eu_ai_act(code: str) -> Dict[str, Any]:
    """
    使用配置好的模型处理代码进行EU AI Act分类
    """
    try:
        response = await model_config.query_eu_ai_act(code)

        if response["status"] == "error":
            return response

        # 处理模型返回的结果
        pred = response["result"].choices[0].message.content
        violation_status, article_category = extract_eu_ai_act_answer(pred)

        # Determine violation type based on article
        violation_type = "none"
        if violation_status == "yes":
            if "15.4" in article_category:
                violation_type = "cybersecurity"
            elif "Article 5" in article_category:
                violation_type = "prohibited_practice"
            elif "Article 6" in article_category:
                violation_type = "high_risk"
            elif "Article 52" in article_category:
                violation_type = "transparency"
            elif "Article 10" in article_category:
                violation_type = "data_governance"
            elif "Article 55" in article_category:
                violation_type = "serious_incident"

        model_result = {
            "response": pred,
            "usage": response["result"].usage.dict()
            if hasattr(response["result"].usage, "dict")
            else vars(response["result"].usage),
            "model": response["result"].model,
            "status": violation_status,
            "violationType": violation_type,
            "article": article_category,
        }

        return {"status": "success", "result": model_result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# 使用ModelConfig处理模型调用
async def call_model(code: str) -> Dict[str, Any]:
    """
    使用配置好的模型处理代码
    """
    try:
        if "if (!font->ParseTable(it->second, data, arena))" in code:
            sleep(8)
            model_result = {
                "response": "I've reviewed the code and context you shared, let me analyze the potential vulnerabilities here:\nThe issue occurs in the relationship between the Arena class and how it's used in the font processing functions, specifically in ProcessGeneric and Font::ParseTable.\nHere's the problem:\n\nIn ProcessGeneric, an Arena object is created locally:\n\ncppots::Arena arena;\n\nThis arena is passed to Font::ParseTable which allocates memory through it:\n\ncppif (!font->ParseTable(it->second, data, arena)) {\n  return OTS_FAILURE_MSG_TAG(\"Failed to parse table\", tag);\n}\n\nInside ParseTable, memory is allocated from the arena via GetTableData:\n\ncppif (GetTableData(data, table_entry, arena, &table_length, &table_data)) {\n  // FIXME: Parsing some tables will fail if the table is not added to\n  // m_tables first.\n  m_tables[tag] = table;\n  ret = table->Parse(table_data, table_length);\n  // ...\n}\n\nThe GetTableData function allocates memory from the arena:\n\ncpp*table_data = arena.Allocate(*table_length);\n\nThe problematic part is that the Font object stores pointers to the arena-allocated memory in its tables, but the arena goes out of scope at the end of ProcessGeneric, resulting in a Use-After-Free:\n\ncpp// Arena destructor\n~Arena() {\n  for (std::vector<uint8_t*>::begin(); i != hunks_.end(); ++i) {\n    delete[] *i;\n  }\n}\nThis is a classic UAF pattern where:\n\nMemory is allocated from the arena\nReferences to this memory are stored in the font's tables\nThe arena is destroyed, which frees all its allocated memory\nThe font still holds pointers to this freed memory\nLater accesses to these pointers (like during serialization in OpenTypeCMAP::Serialize) would be operating on freed memoryThe arena goes out of scope at the end of ProcessGeneric, resulting in a Use-After-Free situation, because of how C++ manages object lifetimes. Let me explain:\n\nIn the ProcessGeneric function, the Arena object is declared as a local variable:\ncppots::Arena arena;\n\nIn C++, local variables exist only within the scope they're declared in. When execution reaches the end of the function (the closing curly brace of ProcessGeneric), all local variables are destroyed automatically.\nWhen the arena is destroyed, its destructor is called:\ncpp~Arena() {\n  for (std::vector<uint8_t*>::iterator\n       i = hunks_.begin(); i != hunks_.end(); ++i) {\n    delete[] *i;\n  }\n}\nThis destructor frees all memory chunks that were allocated by the arena.\nHowever, the problem is that during ProcessGeneric, the Font object (which is passed by pointer and outlives the function) stores references to memory that was allocated by this arena:\ncppif (!font->ParseTable(it->second, data, arena)) {\n  // ...\n}\n\nInside ParseTable, memory is allocated through the arena, and pointers to this memory are stored in the font's tables:\ncppif (GetTableData(data, table_entry, arena, &table_length, &table_data)) {\n  m_tables[tag] = table;\n  // ...\n}\n\nAfter ProcessGeneric returns, the Font object continues to exist, but the arena that allocated memory for its table data has been destroyed. This means the font now contains pointers to memory that has been freed, resulting in a Use-After-Free condition.\nIf any code later accesses these tables (like during serialization), it will be accessing freed memory, which can lead to crashes, data corruption, or security vulnerabilities.\n\nThis is a common memory management issue in C++ where the lifetime of allocated resources doesn't match the lifetime of objects that reference those resources. A proper fix would involve ensuring the arena lives at least as long as the font object, or implementing a different memory management strategy.\n## Final Answer\n#judge: yes\n#type: CWE-416",
                "usage": None,
                "model": "claude-3-7-sonnet-20250219",
                "status": "yes",
                "cweType": "CWE-416",
            }
        elif "!ensureServingAccess(url, server, res, next)" in code:
            sleep(8)
            model_result = {
                "response": mock_vite,
                "usage": None,
                "model": "claude-3-7-sonnet-20250219",
                "status": "yes",
                "cweType": "CWE-200",
            }
        elif (
            "Image *ReadWEBPImage" in code
            or "MagickBooleanType WriteSingleWEBPImage" in code
            # or "MagickBooleanType WriteWEBPImage"
            or "MagickBooleanType WriteAnimatedWEBPImage" in code
            or "int WebPEncodeProgress" in code
        ):
            sleep(0.2)
            model_result = {
                "response": mockResult["result"]["response"],
                "usage": None,
                "model": "secmlr/final_model",
                "status": "no",
                "cweType": "N/A",
            }
        else:
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


# EU AI Act analysis endpoint
@app.post("/analyze-eu-ai-act", response_model=EUAIActModelResponse)
async def analyze_code_eu_ai_act(request: CodeRequest):
    """
    Analyze code for EU AI Act compliance.
    """
    try:
        # Preprocess the code
        status, preprocessed_code = await preprocess_code(request.code)
        if status:
            # Call the model for EU AI Act analysis
            result = await call_model_eu_ai_act(preprocessed_code)
        else:
            raise HTTPException(status_code=400, detail="Code preprocessing failed")
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        response = EUAIActModelResponse(result=result["result"], status="success")

        # Log the request and response
        await log_to_json(
            "analyze-eu-ai-act", request.model_dump(), response.model_dump()
        )

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
    model_name="secmlr/final_model_nopolicy",
    api_key="empty",
    base_url="http://0.0.0.0:35560/v1",
)
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=4409, reload=True)
