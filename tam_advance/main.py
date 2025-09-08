import os
import time
from dotenv import load_dotenv

from adk.api import agents
from agent import create_tam_super_agent

def run_agent_scenario(agent: agents.Agent, prompt: str, scenario_title: str):
    """Helper function to run and print a single agent scenario."""
    print("=" * 60)
    print(f"🎬 SCENARIO: {scenario_title}")
    print(f"👤 TAM PROMPT: \"{prompt}\"")
    print("-" * 60)
    
    start_time = time.time()
    response = agent.run(prompt)
    end_time = time.time()
    
    print("\n" + "-" * 20 + " AGENT FINAL SUMMARY " + "-" * 20)
    print(response)
    print(f"\n✅ SCENARIO COMPLETE (Execution time: {end_time - start_time:.2f} seconds)")
    print("=" * 60 + "\n\n")


# --- Main Execution Logic ---
if __name__ == "__main__":
    load_dotenv()
    print("🚀 Initializing Professional TAM Super-Agent...")
    
    # In a real application, this might be a web server or a Pub/Sub listener.
    # Here, we will run a series of predefined prompts to demonstrate capabilities.
    tam_agent = create_tam_super_agent()
    print("✅ Agent Initialized.")

    prompts_to_run = [
        {
            "title": "Proactive Health & Optimization",
            "prompt": "Run a proactive health and cost check for Customer X and draft an email to the internal engineering team with the findings."
        },
        {
            "title": "Issue & Escalation Management",
            "prompt": "We have a P1 incident for Customer Y regarding 'database latency'. Create a support case, notify the incident chat room, and check our knowledge base for post-mortems on similar issues."
        },
        {
            "title": "Strategic Roadmap & QBR",
            "prompt": "Prepare the Q2 2026 QBR deck for Customer Z."
        },
        {
            "title": "New Product Adoption & Launch Planning",
            "prompt": "A new service, 'AlloyDB Omni for Postgres', was just announced. Identify which of my customers are heavy Postgres users and draft an introductory email for them."
        }
    ]

    for scenario in prompts_to_run:
        run_agent_scenario(tam_agent, scenario["prompt"], scenario["title"])
        time.sleep(2) # Pause between scenarios for readability
