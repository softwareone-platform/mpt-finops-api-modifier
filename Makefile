.env:
	cp .env.example .env

.PHONY: api-contract-server
api-contract-server: .env
	uv run fastapi dev app/api_contract.py
