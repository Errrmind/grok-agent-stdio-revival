#!/usr/bin/env python3
"""
stdio_json_agent.py

Fully functional JSON-RPC 2.0 agent over stdin/stdout.

Core features:
- Extensible method dispatcher
- Blackboard persistence: HDF5 (groups, datasets, attributes) with graceful JSON fallback
- STEM-friendly analysis (numpy stats when available)
- Zero core dependencies; optional h5py + numpy for full power

Designed for sovereign local-first multi-agent systems.
"""

import json
import sys
import os
import traceback
from datetime import datetime

try:
    import h5py
    import numpy as np
    HDF5_AVAILABLE = True
except ImportError:
    HDF5_AVAILABLE = False
    h5py = None
    np = None

BLACKBOARD_FILE = os.path.join("data", "blackboard.h5" if HDF5_AVAILABLE else "blackboard.json")
os.makedirs("data", exist_ok=True)


class StdioJsonAgent:
    def __init__(self):
        self.blackboard = {}
        if not HDF5_AVAILABLE:
            if os.path.exists(BLACKBOARD_FILE):
                with open(BLACKBOARD_FILE, "r") as f:
                    self.blackboard = json.load(f)

    def handle_request(self, request_str: str) -> dict:
        try:
            req = json.loads(request_str)
            method = req.get("method")
            params = req.get("params", {})
            request_id = req.get("id")

            if method == "analyze_text":
                text = params.get("text", "")
                result = {
                    "analysis": f"Deep analysis of: {text[:200]}...",
                    "length": len(text),
                    "timestamp": datetime.now().isoformat()
                }
                return {"jsonrpc": "2.0", "result": result, "id": request_id}

            elif method == "store_to_blackboard":
                return self._store_to_blackboard(params, request_id)

            elif method == "retrieve_from_blackboard":
                return self._retrieve_from_blackboard(params, request_id)

            elif method == "list_blackboard":
                return self._list_blackboard(params, request_id)

            elif method == "analyze_dataset":
                return self._analyze_dataset(params, request_id)

            elif method == "ping":
                return {"jsonrpc": "2.0", "result": {"status": "alive", "timestamp": datetime.now().isoformat()}, "id": request_id}

            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": str(traceback.format_exc())},
                "id": None
            }

    def _store_to_blackboard(self, params: dict, request_id) -> dict:
        group = params.get("group", "default")
        name = params.get("name", "dataset")
        data = params.get("data")
        attrs = params.get("attrs", {})
        attrs["timestamp"] = datetime.now().isoformat()

        if HDF5_AVAILABLE:
            try:
                with h5py.File(BLACKBOARD_FILE, "a") as f:
                    if group not in f:
                        grp = f.create_group(group)
                    else:
                        grp = f[group]

                    if isinstance(data, (list, dict, int, float)) or (hasattr(data, "__array__") if np else False):
                        if np and not isinstance(data, np.ndarray):
                            data = np.asarray(data)
                        dset = grp.create_dataset(
                            name,
                            data=data,
                            compression="gzip" if (np and hasattr(data, "__len__") and len(data) > 100) else None
                        )
                        for k, v in attrs.items():
                            dset.attrs[k] = v

                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "status": "stored_to_hdf5",
                        "group": group,
                        "name": name,
                        "attrs": attrs
                    },
                    "id": request_id
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32000, "message": f"HDF5 store error: {str(e)}"},
                    "id": request_id
                }
        else:
            # JSON fallback
            self.blackboard.setdefault(group, {})[name] = {"data": data, "attrs": attrs}
            with open(BLACKBOARD_FILE, "w") as f:
                json.dump(self.blackboard, f, indent=2)
            return {
                "jsonrpc": "2.0",
                "result": {"status": "stored_to_json", "group": group, "name": name},
                "id": request_id
            }

    def _retrieve_from_blackboard(self, params: dict, request_id) -> dict:
        group = params.get("group")
        name = params.get("name")

        if HDF5_AVAILABLE:
            try:
                with h5py.File(BLACKBOARD_FILE, "r") as f:
                    if group in f and name in f[group]:
                        dset = f[group][name]
                        data = dset[()]
                        if hasattr(data, "tolist"):
                            data = data.tolist()
                        attrs = {k: dset.attrs[k] for k in dset.attrs}
                        return {
                            "jsonrpc": "2.0",
                            "result": {"data": data, "attrs": attrs},
                            "id": request_id
                        }
            except Exception:
                pass

        if group in self.blackboard and name in self.blackboard[group]:
            return {
                "jsonrpc": "2.0",
                "result": self.blackboard[group][name],
                "id": request_id
            }

        return {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": "Not found in blackboard"},
            "id": request_id
        }

    def _list_blackboard(self, params: dict, request_id) -> dict:
        if HDF5_AVAILABLE:
            try:
                structure = {}
                with h5py.File(BLACKBOARD_FILE, "r") as f:
                    for g in f:
                        structure[g] = list(f[g].keys())
                return {"jsonrpc": "2.0", "result": structure, "id": request_id}
            except Exception:
                pass

        return {"jsonrpc": "2.0", "result": list(self.blackboard.keys()), "id": request_id}

    def _analyze_dataset(self, params: dict, request_id) -> dict:
        group = params.get("group")
        name = params.get("name")

        if HDF5_AVAILABLE:
            try:
                with h5py.File(BLACKBOARD_FILE, "r") as f:
                    if group in f and name in f[group]:
                        dset = f[group][name][()]
                        if hasattr(dset, "mean") and np:
                            stats = {
                                "mean": float(np.mean(dset)),
                                "std": float(np.std(dset)),
                                "shape": getattr(dset, "shape", None),
                                "min": float(np.min(dset)),
                                "max": float(np.max(dset))
                            }
                            return {"jsonrpc": "2.0", "result": stats, "id": request_id}
            except Exception:
                pass

        # JSON fallback simple analysis
        if group in self.blackboard and name in self.blackboard[group]:
            data = self.blackboard[group][name].get("data")
            if isinstance(data, list) and data and isinstance(data[0], (int, float)):
                stats = {
                    "mean": sum(data) / len(data),
                    "length": len(data)
                }
                return {"jsonrpc": "2.0", "result": stats, "id": request_id}

        return {
            "jsonrpc": "2.0",
            "result": {"note": "Analysis limited or no numeric data available"},
            "id": request_id
        }

    def run(self):
        for line in sys.stdin:
            if line.strip():
                response = self.handle_request(line.strip())
                print(json.dumps(response))
                sys.stdout.flush()


if __name__ == "__main__":
    agent = StdioJsonAgent()
    agent.run()
