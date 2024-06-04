import asyncio
from multiplayer_chat.schemas import InputSchema
from naptha_sdk.task import Task
from naptha_sdk.client.node import Node
from typing import Dict
import yaml
import json
from multiplayer_chat.utils import get_logger

logger = get_logger(__name__)

async def run(inputs: InputSchema, worker_nodes, orchestrator_node, flow_run, cfg: Dict):

    # workflow = Workflow("Multiplayer Chat", job)
    task1 = Task(name="olas_prediction_1", fn="olas_prediction", worker_node=worker_nodes[0], orchestrator_node=orchestrator_node, flow_run=flow_run)
    task2 = Task(name="olas_prediction_2", fn="olas_prediction", worker_node=worker_nodes[1], orchestrator_node=orchestrator_node, flow_run=flow_run)

    # Execute both tasks concurrently
    response1_future = asyncio.create_task(task1(prompt=inputs.prompt))
    response2_future = asyncio.create_task(task2(prompt=inputs.prompt))

    # Await both futures to get results
    response1 = await response1_future
    logger.info(f"Response 1: {response1}")

    response2 = await response2_future
    logger.info(f"Response 2: {response2}")

    # json loads response1 and response2
    response1 = json.loads(response1)
    response2 = json.loads(response2)

    combined_response = {
        'p_yes': (response1['p_yes']+response2['p_yes'])/2,
        'p_no': (response1['p_no']+response2['p_no'])/2,
        'confidence': (response1['confidence']+response2['confidence'])/2
    }

    return combined_response

if __name__ == "__main__":
    cfg_path = "multi_olas_prediction/component.yaml"
    with open(cfg_path, "r") as file:
        cfg = yaml.load(file, Loader=yaml.FullLoader)
    args = {
        "prompt": "Will there be an initial public offering on either the Shanghai Stock Exchange or the Shenzhen Stock Exchange before 1 January 2016?",
        "coworkers": "http://node.naptha.ai:7001,http://node1.naptha.ai:7001"
    }
    flow_run = {"consumer_id": "user:18837f9faec9a02744d308f935f1b05e8ff2fc355172e875c24366491625d932f36b34a4fa80bac58db635d5eddc87659c2b3fa700a1775eb4c43da6b0ec270d"}
    inputs = InputSchema(**args)
    orchestrator_node = Node("http://localhost:7001")
    worker_nodes = [Node(coworker) for coworker in args['coworkers'].split(',')]
    response = asyncio.run(run(inputs, worker_nodes, orchestrator_node, flow_run, cfg))
    print(response)
