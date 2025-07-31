
provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "raw_data_lake" {
  name     = "${var.project_id}-raw-zone"
  location = var.region
}

resource "google_bigquery_dataset" "raw_dataset" {
  dataset_id = "raw_data"
  location   = var.region
}

resource "google_bigquery_dataset" "curated_dataset" {
  dataset_id = "curated_data"
  location   = var.region
}

resource "google_pubsub_topic" "stream_topic" {
  name = "streaming-data-topic"
}

resource "google_dataflow_flex_template_job" "streaming_job" {
  name              = "streaming-ingestion-job"
  container_spec_gcs_path = "gs://dataflow-templates/streaming_template.json"
  parameters = {
    inputTopic = "projects/${var.project_id}/topics/${google_pubsub_topic.stream_topic.name}"
    outputTable = "${var.project_id}:${google_bigquery_dataset.raw_dataset.dataset_id}.stream_output"
  }
  on_delete = "cancel"
}
