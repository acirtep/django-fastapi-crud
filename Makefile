
django_app:
	docker compose -f docker-compose-django.yaml  up

django_test:
	docker compose -p django-test -f docker-compose-django-test.yaml  up -d && \
	sleep 2 && \
	docker exec -it django_crud_test python manage.py test --verbosity=2 && \
	docker compose -p django-test down

fastapi_app:
	docker compose -f docker-compose-fastapi.yaml  up

fastapi_test:
	docker compose -p fastapi-test -f docker-compose-fastapi-test.yaml  up -d && \
	sleep 2 && \
	docker exec -it fastapi_crud_test bash -c "alembic downgrade base && alembic upgrade head && python -m pytest -v --asyncio-mode=auto" && \
	docker compose -p fastapi-test down

check:
	pre-commit install --hook-type commit-msg --hook-type pre-push && \
	pre-commit run --all-files

ipython:
	# https://github.com/ipython/ipython/issues/14260
	docker exec -it fastapi_crud bash -c "pip uninstall -y prompt_toolkit; pip install prompt_toolkit; pip install ipython; bash"

load_medium_data:
	docker exec -it fastapi_crud python mysite/utils/load_medium_articles.py
