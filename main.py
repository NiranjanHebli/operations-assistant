import sys
from dotenv import load_dotenv

# Load env vars (importantly CREWAI_TELEMETRY_OPT_OUT) BEFORE anything else
load_dotenv()

# Setup our custom OTel provider BEFORE crewai is imported
from utils.telemetry import setup_telemetry, shutdown_telemetry

setup_telemetry()

# Now it is safe to import crewai and run the crew
from crew.crew import run_crew


def main():
    question = sys.argv[1] if len(sys.argv) > 1 else "What is the return policy?"
    try:
        answer = run_crew(question)
        print("\n FINAL ANSWER :")
        print(answer)
    finally:
        shutdown_telemetry()


if __name__ == "__main__":
    main()
