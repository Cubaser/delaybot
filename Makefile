code_check:
	@echo "Проверяем код"
	ruff check .

code_fix:
	@echo "Проверяем код"
	ruff check . --fix

code_format:
	@echo "Проверяем код"
	ruff format