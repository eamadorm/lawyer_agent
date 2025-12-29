
PROJECT_ID=learned-stone-454021-c8
REGION=us
DOF_PIPELINE_REGION=us-central1

run-agent:
	uv run --group agent -m agent.main

test-dof-pipeline:
	uv run --group dof_pipeline -m pipelines.dof.main --start_date 02/01/2025

deploy-dof-pipeline:
	uv export --group dof_pipeline --no-hashes --format requirements-txt > pipelines/dof/requirements.txt
	gcloud functions deploy dof-scraper-function \
	--gen2 \
	--runtime=python312 \
	--region=$(DOF_PIPELINE_REGION) \
	--source=pipelines/dof \
	--entry-point=scrape_dof_function \
	--trigger-http \
	--set-env-vars=PROJECT_ID=$(PROJECT_ID) \
	--no-allow-unauthenticated \
	--service-account=dof-pipeline@learned-stone-454021-c8.iam.gserviceaccount.com
	rm pipelines/dof/requirements.txt

schedule-dof-pipeline:
	gcloud scheduler jobs create http dof-scrapper-job \
	--location=$(DOF_PIPELINE_REGION) \
	--schedule="0 8 * * *" \
	--time-zone="America/Mexico_City" \
	--http-method=GET \
	--uri=https://us-central1-learned-stone-454021-c8.cloudfunctions.net/dof-scraper-function \
	--oidc-service-account-email=dof-pipeline@learned-stone-454021-c8.iam.gserviceaccount.com