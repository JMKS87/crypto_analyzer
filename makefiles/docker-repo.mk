IMAGE = publisher-panel_app
CONTAINER_REGISTRY_URL = eu.gcr.io/inventory-publisher-panel/$(IMAGE)
BRANCH_FOR_LATEST = master

BRANCH = $(shell git rev-parse --abbrev-ref HEAD)
SHORT_HASH = $(shell git rev-parse --short HEAD)
TAG = $(BRANCH)-$(SHORT_HASH)

.PHONY: push_images
push_images: ## tags and pushes docker images to GCP repository
	docker tag $(IMAGE) $(CONTAINER_REGISTRY_URL):$(TAG)
	docker push $(CONTAINER_REGISTRY_URL):$(TAG)

ifeq ($(BRANCH),$(BRANCH_FOR_LATEST))
	docker tag $(IMAGE) $(CONTAINER_REGISTRY_URL)
	docker push $(CONTAINER_REGISTRY_URL)
endif
