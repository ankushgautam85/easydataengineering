resource "aws_kinesis_firehose_delivery_stream" "stream" {
  name        = var.stream_name
  destination = "s3"

  s3_configuration {
    role_arn           = var.firehose_role_arn
    bucket_arn         = var.bucket_arn
    compression_format = "GZIP"
    buffering_size     = 5
    buffering_interval = 300

    prefix = "data/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}/"

    cloudwatch_logging_options {
      enabled         = true
      log_group_name  = "/aws/kinesisfirehose/${var.stream_name}"
      log_stream_name = "S3Delivery"
    }
  }
}

output "stream_name" {
  value = aws_kinesis_firehose_delivery_stream.stream.name
}
