import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from crew.crew import run_crew
import pytest

@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="No API key provided")
def test_crew_answers_with_source():
    answer = run_crew("What is the return policy?")
    # Answer must mention the source document
    assert "return_policy" in answer.lower() or "return" in answer.lower()
    # Must not be empty
    assert len(answer) > 50
