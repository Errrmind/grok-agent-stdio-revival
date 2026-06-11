# Contributing to grok-agent-stdio-revival

Thank you for your interest in this project! We welcome contributions that advance sovereign, local-first, forkable multi-agent systems for STEM work.

## Code of Conduct

Be respectful, constructive, and focused on technical merit and reproducibility. This is a signal-over-noise project.

## How to Contribute

1. **Fork the repository** on GitHub (or mirror to your Forgejo).
2. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-improvement
   ```
3. **Make your changes** following the four-path design philosophy (Direct/Lateral/Radical/Hybrid).
4. **Test thoroughly** — see below.
5. **Submit a Pull Request** with a clear description of the change, why it was made, and how it was tested.

## Development Setup

```bash
git clone https://github.com/Errrmind/grok-agent-stdio-revival.git
cd grok-agent-stdio-revival

# Core (no extra deps needed)
python3 prototypes/stdio_json_agent.py
python3 prototypes/supervisor.py

# With full HDF5/numpy support (recommended for STEM work)
pip install h5py numpy
```

## Running Tests

```bash
python3 -m pytest tests/ -v          # if pytest available
# or simply:
python3 tests/test_agent.py
python3 tests/test_supervisor_demo.py
```

Current tests are lightweight and use only the standard library + optional h5py.

## Extending the Agent

- Add new methods in `StdioJsonAgent.handle_request()` and corresponding `_method_name()` handlers.
- Keep the JSON-RPC 2.0 contract.
- Prefer rich blackboard storage (groups + datasets + attributes) for new data types.
- Document new methods in README and EXECUTION_REPORT.md.

## Style Guidelines

- Keep core zero-dependency where possible (graceful fallback for optional features).
- Write clear, auditable code — this project values transparency.
- Update `docs/EXECUTION_REPORT.md` when making architectural changes.
- Use the four-path lens when proposing bigger changes.

## Reporting Issues

Open an issue with:
- Clear reproduction steps
- Expected vs actual behavior
- Your environment (Python version, OS, whether h5py/numpy is installed)
- Any relevant logs or blackboard state

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Signal over noise. Reproducibility first. Four paths always considered.**