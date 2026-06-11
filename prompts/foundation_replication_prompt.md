# Prompt: Foundation Replication + Extension (Optimized for Grok Heavy 4.0)

```markdown
You are an expert sovereign systems architect specializing in local-first, forkable AI infrastructure with deep expertise in pre-API patterns, blackboard architectures, and minimal-dependency agent orchestration.

**Reference Implementation**: The grok-agent-stdio-revival repository (https://github.com/Errrmind/grok-agent-stdio-revival). Study the architecture: stdio JSON-RPC control plane + HDF5/JSON blackboard data plane + supervisor-orchestrated 8 specialized agents + Four-Path design philosophy.

**Task**: Create a complete, production-hardened evolution of this system tailored for **[INSERT YOUR DOMAIN, e.g. "personal research automation and knowledge compounding"]**.

**Strict Requirements**:
- Maintain **zero cloud dependencies** for the core system
- Significantly improve the supervisor (proper asyncio + task queue + health checks + exponential backoff)
- Design and implement 3 new specialized agent roles highly relevant to the chosen domain
- Create a richer, versioned blackboard schema with provenance, confidence scores, and dependency tracking
- Include a practical testing strategy that works with and without h5py/numpy
- Provide a clear migration/upgrade path from the v0.1 reference implementation

**Reasoning Framework**: Explicitly use the Four-Path lens (Direct / Lateral / Radical / Hybrid) when making architectural decisions. Document why you chose each approach.

**Output Format** (clean, copy-paste ready):
1. Updated high-level architecture diagram (Mermaid or ASCII)
2. Full recommended directory structure
3. Key modified or new code files (especially supervisor.py and new agent role examples)
4. Blackboard schema definition (with example groups/datasets/attributes)
5. Architecture Decision Record (ADR) explaining the major choices
6. Recommended next 3 evolution steps

Prioritize auditability, forkability, and long-term maintainability by a solo developer.
```