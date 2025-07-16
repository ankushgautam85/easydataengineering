variable "bucket_name" {
  type        = string
  description = "Name of the production S3 bucket"
}

variable "firehose_stream_name" {
  type        = string
  description = "Name of the production Firehose stream"
}
