
import sys
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from modules.ai_assistant import generate_research_answer


# Deliberately invalid test evidence.
# The assistant should reject it rather than invent science.
sample_evidence = [
    {
        "experiment_name": "Sample Combustion Experiment",
        "passage": (
            "This is placeholder evidence used to test "
            "the AI assistant's input and output structure."
        ),
        "source_title": "Temporary Test Record",
        "source_url": "",
        "source_type": "test",
        "page_number": None,
    }
]

start = perf_counter()

result = generate_research_answer(
    "What does this experiment tell us about combustion?",
    sample_evidence,
)

elapsed = perf_counter() - start

print("\nANSWER:")
print(result["answer"])

print("\nRESULT STRUCTURE:")
print(result.keys())

print("\nSOURCES:")
print(result["sources"])

print(f"\nLocal response construction: {elapsed:.4f} seconds")

assert elapsed < 1.0, "Local answer construction is unexpectedly slow."
assert result["sources"] == []
assert result["key_findings"] == []
assert "insufficient" in result["answer"].lower() or (
    "could not find usable" in result["answer"].lower()
)

print("\nAll tests passed.")
