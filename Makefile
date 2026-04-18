.PHONY: start stop reset logs status help producer consumer anomaly

help:
	@echo "Prometheus Unbound commands"
	@echo "make start    - Start all services"
	@echo "make stop     - Stop all services"
	@echo "make reset    - Wipe and restart"
	@echo "make logs     - Tail all logs"
	@echo "make status   - Check services"

start:
	cp -n .env.example .env 2>/dev/null || true
	docker-compose up -d

stop:
	docker-compose down

reset:
	docker-compose down -v
	docker-compose up -d

logs:
	docker-compose logs -f

status:
	docker ps --format "table {{.Names}}	{{.Status}}"

producer:
	cd producer && pip install -r requirements.txt -q && python3 generator.py

consumer:
	cd consumer && pip install -r requirements.txt -q && python3 consumer.py

anomaly:
	cd anomaly_engine && pip install -r requirements.txt -q && python3 detector.py
