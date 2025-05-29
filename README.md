# Game Telemetry Pipeline

A serverless pipeline for processing game telemetry events using AWS Lambda. This pipeline handles event deduplication, normalization, and validation of game client events.


## Prerequisites

- Python 3.8 or higher
- AWS Account with appropriate permissions
- AWS CLI configured with your credentials

## Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd game-telemetry-pipeline
```

2. Create a `.env` file:
```env
AWS_REGION=us-east-1
DEDUP_TABLE=game-events-dedup
```

3. Setup development environment:
```bash
make dev-setup
```

## Development Commands

Use these Make commands for development:

```bash
# Setup and Installation
make setup      # Create virtual environment
make install    # Install dependencies
make dev-setup  # Full development setup (install, format, lint)

# Development Workflow
make format     # Format code with black
make lint       # Run type checking with mypy
make test       # Run tests
make coverage   # Run tests with coverage report
make check      # Run all checks (format, lint, test)

# Cleanup and Maintenance
make clean      # Clean up generated files

# Deployment
make package    # Create Lambda deployment package
make deploy     # Deploy to AWS Lambda
```

## AWS Infrastructure Setup

Create the required DynamoDB table:
```bash
aws dynamodb create-table \
    --table-name game-events-dedup \
    --attribute-definitions AttributeName=event_id,AttributeType=S \
    --key-schema AttributeName=event_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --time-to-live-specification "Enabled=true,AttributeName=ttl"
```

## Event Format

```json
{
    "event_type": "player_action",
    "player_id": "player123",
    "game_version": "1.0.0",
    "timestamp": "2024-03-21T12:00:00Z",
    "data": {
        "action": "jump",
        "position": {"x": 100, "y": 200}
    }
}
```
