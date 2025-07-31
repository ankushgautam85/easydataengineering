
output "bucket_name" {
  value = google_storage_bucket.raw_data_lake.name
}

output "raw_dataset_id" {
  value = google_bigquery_dataset.raw_dataset.dataset_id
}

output "curated_dataset_id" {
  value = google_bigquery_dataset.curated_dataset.dataset_id
}
