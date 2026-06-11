#!/usr/bin/env python3
"""
supervisor.py

Central orchestrator for 8 parallel specialized stdio JSON-RPC agents.

Features:
- Spawns agents via subprocess + stdio pipes
- Role-based task routing
- Shared blackboard (HDF5/JSON) for mind-sync
- Built-in multi-agent simulation demonstrating emergent coordination
- Basic retry and result collection

This demonstrates the Hybrid path: Direct stdio + blackboard mind-sync + supervisor orchestration.
"""

import json
import subprocess
import threading
import time
import queue
import os
import random

AGENT_SCRIPT = "prototypes/stdio_json_agent.py"
NUM_AGENTS = 8
AGENT_ROLES = [
    "research_agent", "data_analyzer", "db_persister", "mind_syncer",
    "planner", "reviewer", "validator", "executor"
]


class Supervisor:
    def __init__(self):
        self.task_queue = queue.Queue()
        self.agents = {}
        self.blackboard_lock = threading.Lock()
        self.running = True
        self.results = {}
        os.makedirs("data", exist_ok=True)

    def start_agents(self):
        for i in range(NUM_AGENTS):
            role = AGENT_ROLES[i]
            proc = subprocess.Popen(
                ["python3", AGENT_SCRIPT],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.agents[role] = proc
            t = threading.Thread(
                target=self._read_agent_output, args=(role, proc.stdout), daemon=True
            )
            t.start()
            print(f"Started {role} agent (PID {proc.pid})")
        print(f"\n✅ {NUM_AGENTS} parallel specialized agents launched with shared blackboard mind-sync\n")

    def _read_agent_output(self, role: str, stdout):
        for line in stdout:
            if line.strip():
                try:
                    resp = json.loads(line)
                    if "result" in resp:
                        task_id = resp.get("id")
                        self.results[task_id] = resp["result"]
                        print(f"[{role}] Result received: {str(resp['result'])[:120]}...")
                except Exception:
                    pass

    def send_to_agent(self, role: str, method: str, params: dict, request_id: int = None):
        if role not in self.agents:
            return {"error": "Agent role not found"}
        proc = self.agents[role]
        req = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": request_id or int(time.time() * 1000)
        }
        try:
            proc.stdin.write(json.dumps(req) + "\n")
            proc.stdin.flush()
            time.sleep(0.6)  # Simple wait for demo; replace with proper queue in production
            return self.results.get(req["id"], {"status": "dispatched", "role": role})
        except Exception as e:
            return {"error": str(e)}

    def route_task(self, task_description: str):
        task_lower = task_description.lower()
        if any(kw in task_lower for kw in ["research", "search", "investigate"]):
            role = "research_agent"
            method = "analyze_text"
            params = {"text": task_description}
        elif any(kw in task_lower for kw in ["analyze", "dataset", "stats", "compute"]):
            role = "data_analyzer"
            method = "analyze_dataset"
            params = {"group": "tasks", "name": f"task_{int(time.time())}", "data": task_description}
        elif any(kw in task_lower for kw in ["store", "persist", "save", "blackboard"]):
            role = "db_persister"
            method = "store_to_blackboard"
            params = {
                "group": "mind_sync",
                "name": f"entry_{int(time.time())}",
                "data": task_description,
                "attrs": {"source": "supervisor", "priority": 5}
            }
        elif any(kw in task_lower for kw in ["sync", "mind", "collaborate", "share"]):
            role = "mind_syncer"
            method = "retrieve_from_blackboard"
            params = {"group": "mind_sync", "name": "latest"}
        else:
            role = random.choice(AGENT_ROLES)
            method = "analyze_text"
            params = {"text": task_description}

        return self.send_to_agent(role, method, params)

    def run_simulation(self, num_tasks: int = 6):
        print("\n🚀 Running multi-agent simulation with shared blackboard mind-sync...\n")
        tasks = [
            "Research pre-API Unix pipes and blackboard architectures for agent systems",
            "Analyze sample STEM dataset and store structured results to blackboard",
            "Mind-sync latest research findings across specialized agents",
            "Persist analysis artifacts using HDF5 groups and rich metadata",
            "Review current knowledge state and plan next daily automation cycle",
            "Validate data integrity and execute follow-up knowledge compounding task"
        ]
        for i, task in enumerate(tasks[:num_tasks]):
            print(f"Task {i+1}: {task}")
            result = self.route_task(task)
            print(f"  → Routed to {result.get('role', 'agent')} | Result: {str(result)[:100]}...\n")
            time.sleep(0.8)
        print("✅ Simulation complete. Check data/blackboard.h5 (or .json) for persistent mind-sync state.\n")

    def shutdown(self):
        self.running = False
        for role, proc in self.agents.items():
            try:
                proc.terminate()
            except Exception:
                pass
        print("Supervisor and all agents shut down cleanly.")


if __name__ == "__main__":
    sup = Supervisor()
    sup.start_agents()
    sup.run_simulation()
    time.sleep(3)
    sup.shutdown()
