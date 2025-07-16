output "bucket_arn" {
  value = module.s3_bucket.bucket_arn
}

output "firehose_stream_name" {
  value = module.firehose_stream.stream_name
}
