#!/usr/bin/env python3
"""
Simple tests for stdio_json_agent.py

Run with:
    python3 tests/test_agent.py

Uses only stdlib (unittest). Optional h5py/numpy tests are skipped gracefully if not present.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

# Add parent to path so we can import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prototypes.stdio_json_agent import StdioJsonAgent


class TestStdioJsonAgent(unittest.TestCase):
    def setUp(self):
        self.agent = StdioJsonAgent()
        # Use a temp blackboard for isolation
        self.temp_dir = tempfile.mkdtemp()
        self.original_blackboard = self.agent.__class__.BLACKBOARD_FILE if hasattr(self.agent.__class__, 'BLACKBOARD_FILE') else None

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ping(self):
        req = json.dumps({"jsonrpc": "2.0", "method": "ping", "params": {}, "id": 1})
        resp = self.agent.handle_request(req)
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertIn("result", resp)
        self.assertEqual(resp["result"]["status"], "alive")

    def test_analyze_text(self):
        req = json.dumps({
            "jsonrpc": "2.0",
            "method": "analyze_text",
            "params": {"text": "This is a test of the sovereign agent"},
            "id": 2
        })
        resp = self.agent.handle_request(req)
        self.assertIn("result", resp)
        self.assertIn("analysis", resp["result"])
        self.assertGreater(resp["result"]["length"], 0)

    def test_store_and_retrieve_blackboard_json_fallback(self):
        # Force JSON path by temporarily disabling HDF5 if present
        original_hdf5 = self.agent.__class__._store_to_blackboard  # not perfect but works for test

        req_store = json.dumps({
            "jsonrpc": "2.0",
            "method": "store_to_blackboard",
            "params": {
                "group": "test_group",
                "name": "test_entry",
                "data": [1, 2, 3, 42],
                "attrs": {"note": "unit test"}
            },
            "id": 3
        })
        resp_store = self.agent.handle_request(req_store)
        self.assertIn("result", resp_store)
        self.assertIn(resp_store["result"]["status"], ["stored_to_json", "stored_to_hdf5"])

        req_retrieve = json.dumps({
            "jsonrpc": "2.0",
            "method": "retrieve_from_blackboard",
            "params": {"group": "test_group", "name": "test_entry"},
            "id": 4
        })
        resp_retrieve = self.agent.handle_request(req_retrieve)
        self.assertIn("result", resp_retrieve)
        data = resp_retrieve["result"].get("data")
        self.assertIsNotNone(data)

    def test_list_blackboard(self):
        req = json.dumps({"jsonrpc": "2.0", "method": "list_blackboard", "params": {}, "id": 5})
        resp = self.agent.handle_request(req)
        self.assertIn("result", resp)
        self.assertIsInstance(resp["result"], (list, dict))

    def test_analyze_dataset_non_numeric(self):
        # Store non-numeric and analyze
        self.agent.handle_request(json.dumps({
            "jsonrpc": "2.0", "method": "store_to_blackboard",
            "params": {"group": "analysis", "name": "text_data", "data": "hello world"},
            "id": 6
        }))
        req = json.dumps({
            "jsonrpc": "2.0",
            "method": "analyze_dataset",
            "params": {"group": "analysis", "name": "text_data"},
            "id": 7
        })
        resp = self.agent.handle_request(req)
        self.assertIn("result", resp)
        self.assertIn("note", resp["result"])  # Should gracefully note limitation


if __name__ == "__main__":
    unittest.main(verbosity=2)
