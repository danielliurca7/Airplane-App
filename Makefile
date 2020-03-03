build:
	docker-compose -f .\deployment.yaml build

run:
	docker-compose -f .\deployment.yaml up -d

clean:
	docker-compose -f .\deployment.yaml down --volumes
	docker rmi tema2_client tema2_airplane tema2_admin tema2_mysql