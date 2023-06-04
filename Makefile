run-local: 
	docker run -p 8501:8501 --env-file ./.env --rm job-search-engine