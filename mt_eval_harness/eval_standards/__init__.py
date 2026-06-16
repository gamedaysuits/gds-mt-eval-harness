"""
Evaluation Standards — Language-specific metric plugins loaded by the harness.

Each language with custom evaluation logic gets a sub-package here
(e.g., eval_standards.crk for Plains Cree LYSS). The harness discovers
and loads these via the language card's evalMetrics declaration.

WHY THIS EXISTS:
    Evaluation standards are the REFEREE — they must live in the harness,
    not in any contestant's method plugin. A metric that lives inside one
    translation method's directory can't fairly score other methods.

ARCHITECTURE:
    Language cards (the SSOT) declare evalMetrics with module paths like
    "eval_standards.crk.metrics". plugin_discovery.py uses importlib to
    load the declared classes at runtime. This keeps the harness generic:
    adding eval standards for a new language requires:
        1. A sub-package here (eval_standards/xyz/)
        2. An evalMetrics declaration on the language card (xyz.json)
        3. Zero changes to harness core code
"""
