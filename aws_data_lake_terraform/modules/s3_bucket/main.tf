resource "aws_s3_bucket" "data_lake" {
  bucket = var.bucket_name

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  lifecycle_rule {
    id      = "lifecycle"
    enabled = true

    expiration {
      days = 365
    }

    noncurrent_version_expiration {
      days = 90
    }
  }

  tags = {
    Name        = var.bucket_name
    Environment = "prod"
  }
}

output "bucket_arn" {
  value = aws_s3_bucket.data_lake.arn
}
