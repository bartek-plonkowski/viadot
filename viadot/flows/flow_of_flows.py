from typing import Any, Dict, List

from prefect import Flow, Task, apply_map
from prefect.tasks.prefect import StartFlowRun
from prefect.exceptions import PrefectException


class Pipeline(Flow):
    def __init__(
        self,
        name: str,
        project_name: str,
        extract_flows_names: List[str],
        transform_flow_names: List[str],
        *args: List[any],
        **kwargs: Dict[str, Any]
    ):
        self.extract_flows_names = extract_flows_names
        self.transform_flow_names = transform_flow_names
        self.project_name = project_name
        super().__init__(*args, name=name, **kwargs)
        self.gen_flow()

    def gen_start_flow_run_task(self, flow_name: str, flow: Flow = None) -> Task:
        flow_extract_run = StartFlowRun(wait=True)
        t = flow_extract_run.bind(
            flow_name=flow_name, project_name=self.project_name, flow=flow
        )
        return t

    def gen_flow(self) -> Flow:
        extract_flow_runs = apply_map(
            self.gen_start_flow_run_task, self.extract_flows_names, flow=self
        )
        transform_flow_runs = apply_map(
            self.gen_start_flow_run_task, self.transform_flow_names, flow=self
        )
        transform_flow_runs.set_upstream(extract_flow_runs, flow=self)
