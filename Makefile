
PROJECT_ID=learned-stone-454021-c8
REGION=us

run-agent:
	uv run --group agent -m agent.main

test-dof-pipeline:
	uv run --group dof_pipeline -m pipelines.dof.main --start_date 02/01/2025

deploy-dof-pipeline:
	uv export --group dof_pipeline --no-hashes --format requirements-txt > pipelines/dof/requirements.txt
	gcloud functions deploy dof-scraper-function \
	--gen2 \
	--runtime=python312 \
	--region=$(REGION) \
	--source=pipelines/dof \
	--entry-point=scrape_dof_function \
	--trigger-http \
	--allow-unauthenticated \
	--set-env-vars=PROJECT_ID=$(PROJECT_ID) \
	--service-account="dof-pipeline@learned-stone-454021-c8.iam.gserviceaccount.com"
	rm pipelines/dof/requirements.txt