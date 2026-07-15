# ingest only clean data
python -m app.ingestion.processor DATA/true_data true

# Ingest only 10 noisy files
python -m app.ingestion.processor DATA/noisy_sample_10 noisy

# Ingest only 15 noisy files
python -m app.ingestion.processor Data/noisy_sample_15 noisy