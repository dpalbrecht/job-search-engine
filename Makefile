run-local: 
	docker run -p 8501:8501 --env-file ./.env --rm job-search-engine

tag-push:
	aws ecr get-login-password | docker login --username AWS --password-stdin 838424036277.dkr.ecr.us-west-1.amazonaws.com
	docker tag job-search-engine:latest 838424036277.dkr.ecr.us-west-1.amazonaws.com/job-search-engine:latest
	docker push 838424036277.dkr.ecr.us-west-1.amazonaws.com/job-search-engine:latest

pull:
	aws ecr get-login-password | docker login --username AWS --password-stdin 838424036277.dkr.ecr.us-west-1.amazonaws.com
	docker pull 838424036277.dkr.ecr.us-west-1.amazonaws.com/job-search-engine:latest

run-prod:
	docker run -p 8501:8501 --env-file ./.env 838424036277.dkr.ecr.us-west-1.amazonaws.com/job-search-engine