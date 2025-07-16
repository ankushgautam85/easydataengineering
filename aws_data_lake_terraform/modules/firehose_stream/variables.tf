variable "stream_name" {
  type        = string
  description = "Name of the delivery stream"
}

variable "bucket_arn" {
  type        = string
  description = "ARN of the target S3 bucket"
}

variable "firehose_role_arn" {
  type        = string
  description = "IAM role ARN for Firehose"
}
