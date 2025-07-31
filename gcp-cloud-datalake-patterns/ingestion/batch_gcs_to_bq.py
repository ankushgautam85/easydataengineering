from google.cloud import bigquery

def load_csv_to_bq(uri, dataset_id, table_id):
    client = bigquery.Client()
    table_ref = client.dataset(dataset_id).table(table_id)
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1
    )
    load_job = client.load_table_from_uri(uri, table_ref, job_config=job_config)
    load_job.result()
    print(f"Loaded {uri} into {dataset_id}.{table_id}")
