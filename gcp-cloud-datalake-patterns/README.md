# ☁️ GCP Cloud Datalake Patterns

This repository provides modular, production-ready data lake patterns on Google Cloud Platform (GCP) focusing on **data ingestion** and **data transformation** using GCP-native services.

## 🔧 Architecture Patterns

### 1. Batch Ingestion: Cloud Storage → BigQuery

```
┌────────────┐    ┌────────────────────┐    ┌──────────────┐
│ Data Files │ -> │ Cloud Storage (GCS)│ -> │ Batch Loader │
└────────────┘    └────────────────────┘    │  (Dataflow)  │
                                             └──────┬───────┘
                                                    ↓
                                             ┌──────────────┐
                                             │  BigQuery    │
                                             └──────────────┘
```

...

See full README in repo for more patterns and guidance.
