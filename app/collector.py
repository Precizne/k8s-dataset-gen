import os
import json
import time
import threading
import requests

PROMETHEUS_URL = os.environ.get("PROMETHEUS_URL", "http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090")
PROMETHEUS_QUERIES = os.environ.get("PROMETHEUS_QUERIES", "[]")
DATASET_FILE = os.environ.get("DATASET_FILE", "/data/dataset.json")
COLLECTION_INTERVAL = int(os.environ.get("COLLECTION_INTERVAL", "30"))

dataset = []

def fetch_metrics_for_query(name, query):
    entries = []
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
        response.raise_for_status()
        result = response.json()
        if result.get("status") != "success":
            print(f"Non-success status from Prometheus for query '{query}'")
            return entries
        now = time.time()
        for item in result["data"]["result"]:
            value = item["value"][1]
            metric = item["metric"]
            entry = {
                "timestamp": now,
                "query": query,
                "metric_name": name,
                "labels": metric,
                "value": value
            }
            entries.append(entry)
    except Exception as e:
        print(f"Error fetching metrics for query '{query}':", e)
    return entries

def fetch_metrics():
    queries = json.loads(PROMETHEUS_QUERIES)
    for q in queries:
        entries = fetch_metrics_for_query(q["name"], q["query"])
        for entry in entries:
            dataset.append(entry)
            append_to_json(entry)

def append_to_json(entry):
    if os.path.exists(DATASET_FILE):
        try:
            with open(DATASET_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    else:
        data = []
    data.append(entry)
    with open(DATASET_FILE, "w") as f:
        json.dump(data, f, indent=2)

def collect_periodically():
    while True:
        fetch_metrics()
        time.sleep(COLLECTION_INTERVAL)

def start_background_collector():
    thread = threading.Thread(target=collect_periodically, daemon=True)
    thread.start()

def get_dataset():
    return dataset

def manual_collect():
    fetch_metrics()
    return {"status": "collected"}
