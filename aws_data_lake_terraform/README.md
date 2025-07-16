# AWS Data Lake Terraform Setup

This project provisions a cloud-native, real-time AWS Data Lake architecture using Terraform. It creates:

- An encrypted, versioned S3 bucket with lifecycle rules
- IAM roles with least-privilege permissions
- A Kinesis Data Firehose stream for real-time ingestion
- A dynamic partitioning path (year/month/day/hour) for S3 objects

## 📁 Folder Structure

```
aws_data_lake_terraform/
├── README.md
├── main.tf
├── variables.tf
├── outputs.tf
├── modules/
│   ├── s3_bucket/
│   │   ├── main.tf
│   │   └── variables.tf
│   ├── iam_role/
│   │   ├── main.tf
│   │   └── variables.tf
│   └── firehose_stream/
│       ├── main.tf
│       └── variables.tf
└── environments/
    └── prod/
        ├── main.tf
        ├── variables.tf
        └── terraform.tfvars
```

## 🚀 Usage

```bash
cd environments/prod
terraform init
terraform plan
terraform apply
```

## 🌐 Requirements

- Terraform v1.5+
- AWS CLI configured with permissions to create IAM, S3, Kinesis

