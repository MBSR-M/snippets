#!/usr/bin/env python3
# coding=utf-8


import json
import os
from datetime import datetime

from fastapi import FastAPI, APIRouter
from typing import Dict

# Initialize the FastAPI app
app = FastAPI(title="Dynamic Payload API", description="An API to handle dynamic JSON payloads.")

# Define a router
router = APIRouter()

today = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
dir_path = '/home/callback-jobs/'
os.makedirs(dir_path, exist_ok=True)


# Define the POST endpoint with the router
@router.post("/cyanconnode-test-callback/", summary="Handle dynamic payload",
             description="Accepts and processes any JSON payload.")
async def handle_payload(payload: Dict):
    job_name = payload.get("jobName", "unknown-job")
    try:
        file_path = os.path.join(dir_path, f"{job_name}-{today}.json")
        print(file_path)
        with open(file_path, "w") as file:
            json.dump(payload, file, indent=4)
        return {"success": True, "message": f"Payload saved as {job_name}-{today}.json on path : {file_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

app.include_router(router)
