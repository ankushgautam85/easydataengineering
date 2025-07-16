// Root module to call environment
module "s3_bucket" {
  source      = "./modules/s3_bucket"
  bucket_name = var.bucket_name
}

module "iam_role" {
  source       = "./modules/iam_role"
  bucket_arn   = module.s3_bucket.bucket_arn
}

module "firehose_stream" {
  source             = "./modules/firehose_stream"
  stream_name        = var.firehose_stream_name
  bucket_arn         = module.s3_bucket.bucket_arn
  firehose_role_arn  = module.iam_role.role_arn
}
