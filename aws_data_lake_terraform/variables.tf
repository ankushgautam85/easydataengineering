variable "bucket_name" {
  description = "Name of the S3 data lake bucket"
  type        = string
}

variable "firehose_stream_name" {
  description = "Name of the Firehose delivery stream"
  type        = string
}
