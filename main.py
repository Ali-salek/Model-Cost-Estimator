import argparse
from dataclasses import dataclass

# Command Line Arguments

parser = argparse.ArgumentParser(description="AI Model Selector and Cost Estimator")

parser.add_argument("--task", choices=["summarization", "qa", "content", "coding"], default="qa", help="Type of task")

parser.add_argument("--privacy", choices=["low", "medium", "high"], default="medium", help="Required privacy level")

parser.add_argument("--ram", type=int, default=16, help="Available RAM in GB")

parser.add_argument("--requests", type=int, default=1000, help="Monthly number of requests")

parser.add_argument("--input-tokens", type=int, default=1000, help="Average input tokens per request")

parser.add_argument("--output-tokens", type=int, default=300, help="Average output tokens per request")

parser.add_argument("--budget", type=float, default=16.0, help="Monthly budget in USD")

parser.add_argument("--check-ollama", action="store_true", help="Check local Ollama models")

args = parser.parse_args()


# Data Classes: simple containers for structured data

@dataclass
class Model:
    name: str
    provider: str
    local: bool
    ram_required: int
    context_window: int
    input_price: float
    output_price: float
    tasks: list[str]

@dataclass
class Requirements:
    task: str
    privacy: str
    ram: int
    requests: int
    input_tokens: int
    output_tokens: int
    budget: float

# Model Catalog

MODELS = [
    Model(
        name="Cloud-General",
        provider="Cloud",
        local=False,
        ram_required=0,
        context_window=128_000,
        input_price=1.0,
        output_price=4.0,
        tasks=["summarization", "qa", "content", "coding"],
    ),

    Model(
        name="Cloud-Coder",
        provider="Cloud",
        local=False,
        ram_required=0,
        context_window=128_000,
        input_price=1.5,
        output_price=6.0,
        tasks=["coding", "content"],
    ),

    Model(
        name="Local-Small",
        provider="Ollama",
        local=True,
        ram_required=8,
        context_window=32_000,
        input_price=0,
        output_price=0,
        tasks=["qa", "summarization"],
    ),

    Model(
        name="Local-Coder",
        provider="Ollama",
        local=True,
        ram_required=16,
        context_window=32_000,
        input_price=0,
        output_price=0,
        tasks=["coding", "qa"],
    ),

    Model(
        name="Local-Large",
        provider="Ollama",
        local=True,
        ram_required=32,
        context_window=128_000,
        input_price=0,
        output_price=0,
        tasks=["summarization", "qa", "content", "coding"],
    ),
]

# Monthly Token Calculation

def calculate_monthly_tokens(requirements):
    monthly_input = (requirements.requests * requirements.input_tokens)

    monthly_output = (requirements.requests * requirements.output_tokens)

    return monthly_input, monthly_output

# Cost Calculation

def calculate_cost(model, requests, input_tokens, output_tokens):
    monthly_input = requests * input_tokens
    monthly_output = requests * output_tokens

    input_cost =  (monthly_input / 1_000_000) * model.input_price

    output_cost = (monthly_output / 1_000_000) * model.output_price

    return input_cost + output_cost

# Score Calculation

def calculate_score(model, requirements):
    # Task Score: 30
    if requirements.task in model.tasks:
        task_score = 30
    else:
        task_score = 0
        
    # Privacy Score: 25
    privacy_scores = {
        "high": {"local": 25,"cloud": 5},
        "medium": {"local": 20,"cloud": 15},
        "low": {"local": 10,"cloud": 20}
    }

    provider_type = ("local" if model.local else "cloud")

    privacy_score = privacy_scores[requirements.privacy][provider_type]

    # RAM Score: 20
    if model.ram_required <= requirements.ram:
        ram_score = 20
    else:
        ram_score = -20

    # Context Score: 15
    if model.context_window >= requirements.input_tokens:
        context_score = 15
    else:
        context_score = -15

    # Cost Score: 10
    cost = calculate_cost(model ,requirements.requests ,requirements.input_tokens ,requirements.output_tokens)

    if cost <= requirements.budget:
        cost_score = 10

    elif cost <= requirements.budget * 1.2:
        cost_score = 3

    else:
        cost_score = 0

    # Total Score
    total_score = (task_score + privacy_score + ram_score + context_score + cost_score)

    total_score = max(0, total_score)

    return total_score


# Ollama Check

def check_ollama():

    try:
        from urllib.request import urlopen
        import json

        url = "http://localhost:11434/api/tags"

        with urlopen(url, timeout=2) as response:
            data = json.loads(response.read().decode("utf-8"))

        models = data.get("models", [])

        print("\n=== Ollama ===")
        print("Ollama is available.")

        if not models:
            print("No local models found.")
            return

        print("Installed models:")

        for model in models:
            print(f"  - {model.get('name', 'Unknown')}")

    except Exception:
        print("\n=== Ollama ===")
        print("Warning: Ollama is not available.", "Local model detection skipped.")


# Print Results

def print_results(requirements, monthly_input, monthly_output, results):

    print("\n" + "=" * 50)
    print("AI MODEL SELECTOR")
    print("=" * 50)

    print(f"Task: {requirements.task}")
    print(f"Privacy: {requirements.privacy}")
    print(f"RAM: {requirements.ram} GB")
    print(f"Monthly requests: "f"{requirements.requests}")

    print(f"Input tokens/request: "f"{requirements.input_tokens}")

    print(f"Output tokens/request: "f"{requirements.output_tokens}")

    print(f"Budget: "f"${requirements.budget:.2f}")

    print("\n" + "-" * 50)
    print("MONTHLY TOKEN USAGE")
    print("-" * 50)

    print(f"Input tokens:  {monthly_input:,}")

    print(f"Output tokens: {monthly_output:,}")

    print(f"Total tokens:  "f"{monthly_input + monthly_output:,}")

    print("\n" + "-" * 50)
    print("TOP 3 MODELS")
    print("-" * 50)

    for index, result in enumerate(results[:3], start=1):

        model = result["model"]
        cost = result["cost"]
        score = result["score"]

        print(f"\n{index}. {model.name}")

        print(f"Provider: {model.provider}")

        print(f"Score: "f"{score}/100")

        print(f"Estimated cost: "f"${cost:.2f}")

        print(f"Required RAM: "f"{model.ram_required} GB")

        print(f"Context window: "f"{model.context_window:,}")

        print("Reasons:")

        if requirements.task in model.tasks:
            print("   + Suitable for this task")
        else:
            print("   - Not optimized for this task")

        if model.local:
            if requirements.privacy == "high":
                print("   + Local model is suitable for high privacy")
            else:
                print("   + Runs locally")
        else:
            if requirements.privacy == "high":
                print("   - Cloud model provides less privacy")

            else:
                print("   + Cloud model")

        if model.ram_required <= requirements.ram:
            print("   + Available RAM is sufficient")
        else:
            print(f"   - Not enough RAM \n (requires {model.ram_required} GB)")

        if model.context_window >= requirements.input_tokens:
            print("   + Context window is sufficient")
        else:
            print("   - Context window is too small")

        if cost <= requirements.budget:
            print("   + Within monthly budget")
        else:
            print("   - Exceeds monthly budget")


# =========================
# Main
# =========================

def main():

    requirements = Requirements(task=args.task, privacy=args.privacy, ram=args.ram, requests=args.requests, input_tokens=args.input_tokens, output_tokens=args.output_tokens, budget=args.budget)

    # Check Ollama if requested
    if args.check_ollama:
        check_ollama()

    # Calculate monthly tokens
    monthly_input, monthly_output = (calculate_monthly_tokens(requirements))

    # Calculate cost and score
    results = []

    for model in MODELS:

        cost = calculate_cost(model, requirements.requests, requirements.input_tokens, requirements.output_tokens)

        score = calculate_score(model,requirements)

        results.append({"model": model,"cost": cost,"score": score})

    # Sort by score
    results.sort(key=lambda result: result["score"],reverse=True)

    # Print final results
    print_results(requirements, monthly_input, monthly_output, results)

# Program Entry Point

if __name__ == "__main__":
    main()
