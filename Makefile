
PROJECT_ID=learned-stone-454021-c8
REGION=us
DOF_PIPELINE_REGION=us-central1
LAWYER_AGENT_REGION=us-central1
ARMOR_TEMPLATE_ID=agent-template
AGENT_DATASET=lawyer_app
ARTIFACT_REGISTRY_NAME=ai-agents
AGENT_API_IMAGE_NAME=$(LAWYER_AGENT_REGION)-docker.pkg.dev/$(PROJECT_ID)/$(ARTIFACT_REGISTRY_NAME)/lawyer-agent-api:1.0.0
FRONTEND_IMAGE_NAME=$(LAWYER_AGENT_REGION)-docker.pkg.dev/$(PROJECT_ID)/$(ARTIFACT_REGISTRY_NAME)/lawyer-agent-frontend:1.0.0

run-agent:
	uv run --group agent -m agent.main

run-agent-api:
	uv run --group agent -m uvicorn agent.api.main:app --host 0.0.0.0 --port 8080 --reload

build-agent-image:
	docker build -f agent/Dockerfile -t $(AGENT_API_IMAGE_NAME) .

push-agent-image:
	docker push $(AGENT_API_IMAGE_NAME)

deploy-agent-image:
	gcloud run deploy lawyer-agent-api \
	--image=$(AGENT_API_IMAGE_NAME) \
	--region=$(DOF_PIPELINE_REGION) \
	--min-instances=0 \
	--service-account=lawyer-agent-api@learned-stone-454021-c8.iam.gserviceaccount.com \
	--allow-unauthenticated \
	--port=8080 \
	--set-env-vars=PROJECT_ID=$(PROJECT_ID),TEMPLATE_ID=$(ARMOR_TEMPLATE_ID),ARMOR_REGION=$(LAWYER_AGENT_REGION),AGENT_DATASET=$(AGENT_DATASET)

build-deploy-agent-api:
	make build-agent-image
	make push-agent-image
	make deploy-agent-image

# --- FRONTEND COMMANDS ---

build-frontend-image:
	docker build -f frontend/Dockerfile -t $(FRONTEND_IMAGE_NAME) frontend

push-frontend-image:
	docker push $(FRONTEND_IMAGE_NAME)

deploy-frontend-image:
	gcloud run deploy lawyer-agent-frontend \
	--image=$(FRONTEND_IMAGE_NAME) \
	--region=$(LAWYER_AGENT_REGION) \
	--allow-unauthenticated \
	--port=80

build-deploy-frontend:
	make build-frontend-image
	make push-frontend-image
	make deploy-frontend-image

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
	--timeout=3600s \
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