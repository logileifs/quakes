.PHONY: build

include .env
export

serve:
	uvicorn app.app:app \
		--log-config=${LOG_CONFIG} \
		--ssl-certfile=cert.pem \
		--ssl-keyfile=key.pem \
		--log-level=debug \
		--host=0.0.0.0 \
		--port=${PORT} \
		--reload

build:
	$(eval NEW_BUILD_ID := $(shell openssl rand -hex 3))
	docker build -t logileifs/quakes:latest -t logileifs/quakes:$(NEW_BUILD_ID) .
	$(eval LINE_NUMBER:=$(shell cat .env | grep -n BUILD_ID | cut -f1 -d:))
	@echo $(NEW_BUILD_ID) > ./BUILD
	#@sed -i "$(LINE_NUMBER)s/.*/BUILD_ID=${NEW_BUILD_ID}/" .env
	@sed -i '' "$(LINE_NUMBER)s/.*/BUILD_ID=${NEW_BUILD_ID}/" .env

push:
	# need to include .env again since BUILD_ID might have changed
	$(eval include .env)
	docker push logileifs/quakes:latest
	docker push logileifs/quakes:$(BUILD_ID)

run:
	docker run -p 8000:8000 logileifs/quakes:latest

cert:
	openssl req -nodes -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
