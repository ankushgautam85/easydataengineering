#!/bin/bash
echo "Deploying Dataflow Job..."
python ingestion/stream_pubsub_to_bq.py
