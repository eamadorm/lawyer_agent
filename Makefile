
run-agent:
	uv run --group agent -m agent.main

run-dof-api:
	uv run --group dof_pipeline -m pipelines.dof.main