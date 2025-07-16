module "data_lake" {
  source                = "../.."
  bucket_name           = var.bucket_name
  firehose_stream_name  = var.firehose_stream_name
}
