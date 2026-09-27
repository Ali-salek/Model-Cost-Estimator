# AI Model Selector & Cost Estimator

A command-line tool that recommends the best AI model (cloud or local via Ollama) for your task, based on privacy needs, available RAM, context window requirements, and monthly budget.

## Features

- Compares a catalog of cloud and local (Ollama) models
- Scores each model out of 100 based on:
  - **Task fit** (30 pts) – does the model support your task type?
  - **Privacy** (25 pts) – local models score higher for high-privacy needs
  - **RAM availability** (20 pts) – penalizes models that won't fit your hardware
  - **Context window** (15 pts) – penalizes models that can't fit your input size
  - **Cost** (10 pts) – rewards staying within budget
- Estimates monthly cost from your expected request volume and token usage
- Optionally checks your local Ollama installation for available models
- Prints a ranked top-3 report with reasoning for each recommendation

## Requirements

- Python 3.10+ (uses `list[str]` type hints)
- No external dependencies (standard library only)
- (Optional) [Ollama](https://ollama.com) running locally if you use `--check-ollama`

## Usage

```bash
python project.py [OPTIONS]
```

### Options

| Flag | Type | Default | Description |
|---|---|---|---|
| `--task` | choice | `qa` | Task type: `summarization`, `qa`, `content`, `coding` |
| `--privacy` | choice | `medium` | Privacy level: `low`, `medium`, `high` |
| `--ram` | int | `16` | Available RAM in GB |
| `--requests` | int | `1000` | Expected monthly number of requests |
| `--input-tokens` | int | `1000` | Average input tokens per request |
| `--output-tokens` | int | `300` | Average output tokens per request |
| `--budget` | float | `16.0` | Monthly budget in USD |
| `--check-ollama` | flag | off | Check for locally installed Ollama models |

### Example

```bash
python project.py --task coding --privacy high --ram 32 --requests 2000 --budget 20 --check-ollama
```

This prints:
1. Your input parameters
2. Monthly token usage (input/output/total)
3. The top 3 recommended models, each with a score, estimated cost, and the reasoning behind the score

## Model Catalog

The tool ships with a small built-in catalog (`MODELS` in `project.py`):

| Model | Provider | Local | RAM Required | Context Window |
|---|---|---|---|---|
| Cloud-General | Cloud | No | 0 GB | 128k |
| Cloud-Coder | Cloud | No | 0 GB | 128k |
| Local-Small | Ollama | Yes | 8 GB | 32k |
| Local-Coder | Ollama | Yes | 16 GB | 32k |
| Local-Large | Ollama | Yes | 32 GB | 128k |

You can edit this list directly in `project.py` to add your own models or adjust pricing.

## License

MIT
