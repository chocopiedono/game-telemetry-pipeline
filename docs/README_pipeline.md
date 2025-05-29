# game-telemetry-pipeline
Game Telemetry Pipeline Design
This telemetry pipeline powers business analytics, operational monitoring, and alerts for game event data in Environment A. It ingests, processes, stores, and visualizes high-throughput telemetry from game clients and internal services, with scalable support for up to 1 million daily active users (DAUs).

Ingestion Layer
Game events originate from user clients and are sent to AWS API Gateway, where they are authenticated via:
- Amazon Cognito
- IAM
- Custom Lambda Authorizer  

Pipeline Variants  
There are two variants of the pipeline:

## 1. Lightweight Pipeline
Designed for lower volumes or development/staging environments.

**Flow Overview**:
1) Amazon API Gateway receives events and authenticates requests.
2) Events are written to Amazon Kinesis Data Stream (prod-client-game_event-raw).
3) Kinesis Data Firehose delivers raw events to Amazon S3 (Data Lake – RAW Zone).

A **Lambda function**:
1) Deduplicates events using unique event IDs in Amazon DynamoDB (TTL ~30 minutes).
2) Normalizes, cleans, and filters records.
3) Stores clean data in Amazon DynamoDB (Staging – SILVER Zone).
4) AWS Glue optionally consumes raw Kinesis stream for:  
    1) Spark-based micro-batch processing.
    2) Storage into S3 SILVER Cleaned Zone (normalized and validated).

**Key Benefits:**
1) Native AWS services.
2) Supports both streaming and batch workflows.
3) Cost-efficient and low maintenance.

## 2. Heavyweight Pipeline
Designed for scaling up to 1M+ DAUs and high throughput (~1B+ events/day).

**Estimated Load:**
| Metric | Conservative Estimate | Aggressive Estimate |
|---------------------|----------|-----------|
| Sessions/day        | 2M       | 3M        |
| Events/session      | 300      | 1,000+    |
| Total events/day    | ~600M    | 1B - 3B+  |
| Average event size  | 1 KB     | 1-2KB     |
| Data/day            | ~600 GB  | 1-6 TB    |
| Avg. events/sec     | 6,900    | 35,000    |
| Peak events/sec     | 30,000   | 100,000+  |

**Flow Overview:**  
1. Amazon API Gateway ingests events from:
    1) Game clients
    2) Internal tools
    3) Third-party services
2. Events go into Kinesis Data Stream (ex: prod-client-game_event-raw).
3. Kinesis Firehose stores raw events into Amazon S3 (RAW Zone).
4. Managed Flink jobs:
    1. Deduplicate events with RocksDB-backed stateful processing.
    2. Normalize, clean, and route data to:
        - prod-client-game_event-clean
        - prod-client-game_event-deduped
        - prod-client-game_event-dead-letter (used for alerting)
5. CloudWatch Logs + Prometheus + Grafana:
    - Real-time monitoring and alerting
    - Separate dashboards for streaming operations and analytics
8. AWS Glue / Amazon EMR:
    - Apache Spark streaming jobs for data enrichment
    - Write enriched data into S3 Staging Zone
11. EventBridge + AWS Step Functions:
    - Modular batch transformations into Gold Zone
12. Gold Zone Outputs:
    - Amazon DynamoDB: Fast-access data for internal services
    - Amazon Redshift: BI and ML workloads
    - Amazon S3: Aggregated metrics & logs
    - Amazon RDS: Reporting workloads
13. Amazon QuickSight:
    - Visual dashboards from Redshift and S3
    - Executive-friendly KPIs and product metrics

**Monitoring & Alerting**
1. Amazon CloudWatch provides:
    - Streaming alerts (via Dead Letter Stream monitoring)
    - Operational alerts (via log-based metrics)
2. Grafana Dashboards (via Amazon Managed Service):
    - Operational Streaming Dashboard
    - Business Analytics Dashboard

**Cost Model**
- Pay-as-you-go: costs scale linearly with data volume.
- No long-running infrastructure.
- Fully serverless (where possible), reducing overhead and idle cost.

**Optional Alternatives**
While the current pipeline is 100% AWS-native, it can be optionally rearchitected with:
- Amazon MSK (Kafka)
- Kafka Connect Sinks
- Compatible service ecosystem
However, for simplicity, scalability, and manageability, AWS-native components are the default.

**Diagram Location**
See /docs/telemetry_pipeline_lightweight.png and /docs/telemetry_pipeline_heavyweight.png for architecture visuals.  