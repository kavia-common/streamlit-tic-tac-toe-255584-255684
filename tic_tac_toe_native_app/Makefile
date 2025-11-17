# Makefile for Streamlit Tic Tac Toe (no CMake/Qt; pure Python)
# Common targets used by CI/preview systems

PY := python3
PIP := pip3
PORT ?= 8501

.PHONY: install run start build clean

install:
	$(PIP) install --no-cache-dir -r requirements.txt

run: install
	streamlit run app.py --server.port=$(PORT) --server.address=0.0.0.0

start: run

build: install

clean:
	@echo "Nothing to clean for a pure Streamlit app."
