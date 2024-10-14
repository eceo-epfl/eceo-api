from kubernetes import client, config as k8s_config
from app.config import config
from uuid import UUID
from app.submissions.models import KubernetesExecutionStatus
from typing import Any
from kubernetes.client import CoreV1Api, ApiClient
import subprocess
import os
from cashews import cache
from fastapi.concurrency import run_in_threadpool


def get_k8s_v1() -> client.CoreV1Api | None:
    try:
        list_jobs_runai()
        k8s_config.load_kube_config(config_file=config.KUBECONFIG)
    except Exception:
        return None
    return client.CoreV1Api()


def get_k8s_custom_objects() -> client.CoreV1Api:
    k8s_config.load_kube_config(config_file=config.KUBECONFIG)
    return client.CustomObjectsApi()


def fetch_kubernetes_status():
    """This function contains blocking code to fetch Kubernetes status."""
    try:
        k8s = get_k8s_v1()
        if not k8s:
            raise Exception("Kubernetes client initialization failed")
        ret = k8s.list_namespaced_pod(config.NAMESPACE)
        api = ApiClient()
        k8s_jobs = api.sanitize_for_serialization(ret.items)
        kubernetes_status = True
    except Exception as e:
        print(f"Error fetching Kubernetes status: {e}")
        k8s_jobs = []
        kubernetes_status = False
    return k8s_jobs, kubernetes_status


@cache.early(ttl="30s", early_ttl="10s", key="k8s:status")
async def get_kubernetes_status() -> Any:
    """Offload the blocking Kubernetes status fetch to a thread."""

    print("Fetching Kubernetes status asynchronously")
    return await run_in_threadpool(fetch_kubernetes_status)


def get_jobs_for_submission(
    k8s: CoreV1Api,
    submission_id: UUID,
) -> list[dict[str, Any]]:
    jobs = k8s.list_namespaced_pod(config.NAMESPACE)
    jobs = jobs.items
    jobs = [job for job in jobs if str(submission_id) in job.metadata.name]
    job_status = []
    for job in jobs:
        api = ApiClient()
        job_data = api.sanitize_for_serialization(job)
        job_status.append(
            KubernetesExecutionStatus(
                submission_id=job_data["metadata"].get("name"),
                status=job_data["status"].get("phase"),
                time_started=job_data["status"].get("startTime"),
            )
        )
    return job_status


def delete_job(job_name: str):
    env = os.environ.copy()
    env["KUBECONFIG"] = config.KUBECONFIG
    subprocess.run(
        [
            "runai",
            "delete",
            "job",
            "-p",
            config.PROJECT,
            job_name,
        ],
        env=env,
        check=True,
    )


def list_jobs_runai():
    env = os.environ.copy()
    env["KUBECONFIG"] = config.KUBECONFIG
    result = subprocess.run(
        ["runai", "list", "projects"],
        env=env,
        check=True,
        capture_output=True,
    )
    return result.stdout.decode("utf-8")
