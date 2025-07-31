
# Terraform Setup for GCP Cloud Datalake

This Terraform module sets up:
- Cloud Storage for raw zone
- BigQuery datasets (raw + curated)
- Pub/Sub topic for streaming ingestion
- Dataflow job (templated) to process streaming data

## Usage

```bash
terraform init
terraform apply -var="project_id=your-gcp-project-id"
```
