#!/usr/bin/env python3
"""
Simple, robust tests for stdio_json_agent.py (v0.1.1)

Run:
    python3 tests/test_agent.py

- Uses only stdlib (unittest)
- Gracefully handles missing h5py/numpy
- Tests both success paths and graceful degradation
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prototypes.stdio_json_agent import StdioJsonAgent, BLACKBOARD_FILE, HDF5_AVAILABLE


class TestStdioJsonAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp(prefix="test_blackboard_")
        cls.test_blackboard = os.path.join(cls.temp_dir, "test_blackboard.h5" if HDF5_AVAILABLE else "test_blackboard.json")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def setUp(self):
        self.agent = StdioJsonAgent()
        # Override for test isolation (simple approach for v0.1)
        self.agent.BLACKBOARD_FILE = self.test_blackboard  # type: ignore

    def test_ping(self):
        req = json.dumps({"jsonrpc": "2.0", "method": "ping", "params": {}, "id": 1})
        resp = self.agent.handle_request(req)
        self.assertEqual(resp.get("jsonrpc"), "2.0")
        self.assertIn("result", resp)
        self.assertEqual(resp["result"].get("status"), "alive")

    def test_analyze_text(self):
        req = json.dumps({
            "jsonrpc": "2.0",
            "method": "analyze_text",
            "params": {"text": "Sovereign local-first multi-agent test"},
            "id": 2
        })
        resp = self.agent.handle_request(req)
        self.assertIn("result", resp)
        self.assertIn("analysis", resp["result"])
        self.assertGreaterEqual(resp["result"].get("length", 0), 10)

    def test_store_retrieve_blackboard(self):
        store_req = json.dumps({
            "jsonrpc": "2.0",
            "method": "store_to_blackboard",
            "params": {
                "group": "unit_test",
                "name": "sample_data",
                "data": [10, 20, 30, 99],
                "attrs": {"source": "test", "priority": 8}
            },
            "id": 3
        })
        store_resp = self.agent.handle_request(store_req)
        self.assertIn("result", store_resp)
        status = store_resp["result"].get("status", "")
        self.assertIn(status, ["stored_to_hdf5", "stored_to_json"])

        retrieve_req = json.dumps({
            "jsonrpc": "2.0",
            "method": "retrieve_from_blackboard",
            "params": {"group": "unit_test", "name": "sample_data"},
            "id": 4
        })
        retrieve_resp = self.agent.handle_request(retrieve_req)
        self.assertIn("result", retrieve_resp)
        data = retrieve_resp["result"].get("data")
        self.assertIsNotNone(data)

    def test_list_blackboard(self):
        req = json.dumps({"jsonrpc": "2.0", "method": "list_blackboard", "params": {}, "id": 5})
        resp = self.agent.handle_request(req)
        self.assertIn("result", resp)
        result = resp["result"]
        self.assertTrue(isinstance(result, (list, dict)))

    def test_analyze_dataset_graceful(self):
        # Store string data
        self.agent.handle_request(json.dumps({
            "jsonrpc": "2.0",
            "method": "store_to_blackboard",
            "params": {"group": "graceful", "name": "text_only", "data": "not numeric"},
            "id": 6
        }))
        req = json.dumps({
            "jsonrpc": "2.0",
            "method": "analyze_dataset",
            "params": {"group": "graceful", "name": "text_only"},
            "id": 7
        })
        resp = self.agent.handle_request(req)
        self.assertIn("result", resp)
        # Should not crash; either stats or a note
        self.assertTrue("mean" in resp["result"] or "note" in resp["result"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
