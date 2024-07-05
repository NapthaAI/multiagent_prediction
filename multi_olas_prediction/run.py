import json
from typing import Dict
from naptha_sdk.task import Task
from naptha_sdk.task_engine import run_parallel_tasks
from multi_olas_prediction.schemas import InputSchema
from multi_olas_prediction.utils import get_logger

logger = get_logger(__name__)

async def run(inputs: InputSchema, worker_nodes, orchestrator_node, flow_run, cfg: Dict):
    logger.info(f"Inputs: {inputs}")    
    tasks = [
        Task(
            name=f"olas_prediction_{i+1}", 
            fn="olas_prediction", 
            worker_node=worker_node, 
            orchestrator_node=orchestrator_node, 
            flow_run=flow_run
        )
        for i, worker_node in enumerate(worker_nodes)
    ]

    # Run tasks in parallel
    responses = await run_parallel_tasks(tasks, flow_run, {"prompt": inputs.prompt})

    logger.info(f"Responses: {responses}")
    combined_response = {
        'p_yes': 0,
        'p_no': 0,
        'confidence': 0
    }
    num_responses = 0

    for response in responses:
        res = response.results
        response = json.loads(res[0])
        combined_response['p_yes'] += response['p_yes']
        combined_response['p_no'] += response['p_no']
        combined_response['confidence'] += response['confidence']
        num_responses += 1

    if num_responses > 0:
        combined_response['p_yes'] /= num_responses
        combined_response['p_no'] /= num_responses
        combined_response['confidence'] /= num_responses

    logger.info(f"Combined Response: {combined_response}")
    return combined_response        