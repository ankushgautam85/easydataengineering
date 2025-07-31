import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

class ParseMessageFn(beam.DoFn):
    def process(self, element):
        import json
        record = json.loads(element)
        yield record

def run():
    options = PipelineOptions(
        streaming=True,
        project='your-project-id',
        region='us-central1',
        runner='DataflowRunner',
        temp_location='gs://your-temp-bucket/tmp/'
    )
    with beam.Pipeline(options=options) as p:
        (
            p
            | 'ReadFromPubSub' >> beam.io.ReadFromPubSub(subscription='projects/your-project-id/subscriptions/your-sub')
            | 'ParseJSON' >> beam.ParDo(ParseMessageFn())
            | 'WriteToBigQuery' >> beam.io.WriteToBigQuery(
                table='your-project-id:your_dataset.your_table',
                schema='SCHEMA_AUTODETECT',
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
            )
        )

if __name__ == '__main__':
    run()
