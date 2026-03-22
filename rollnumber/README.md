# Roll Number Submission - Run Guide

This README explains how to run code and tests for all three parts:
`whitebox`, `integration`, and `blackbox`.

## 1. Project Structure

- `whitebox/`: Money-Poly white-box implementation, tests, report
- `integration/`: StreetRace Manager integration implementation, tests, report
- `blackbox/`: QuickCart API black-box tests, report

## 2. One-Time Setup

Run these commands from the `rollnumber` folder:

```bash
cd rollnumber
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install pytest pytest-cov coverage requests pylint
```

If you already use another environment, you can skip creating `.venv`.

## 3. Whitebox (Money-Poly)

### 3.1 Run the code

```bash
cd rollnumber/whitebox/code/moneypoly
python3 main.py
```

### 3.2 Run white-box tests

```bash
cd rollnumber/whitebox
python3 -m pytest tests -q
```

### 3.3 Run branch coverage (Coverage.py)

```bash
cd rollnumber/whitebox
python3 -m coverage erase
python3 -m coverage run --branch -m pytest tests -q
python3 -m coverage report -m
```

## 4. Integration (StreetRace Manager) - Beginner Friendly

This section shows exactly how to run and test the integration module from scratch.

### 4.1 Go to the integration folder

```bash
cd rollnumber/integration
```

### 4.2 Run a basic CLI command (quick check)

This verifies the integration code runs correctly.

```bash
python3 -m code.cli cash-balance
```

Expected result: a line like `Cash balance: 0.00`.

### 4.3 Run common CLI examples

Register a driver:

```bash
python3 -m code.cli register --name Ava --role driver --skill 5
```

Add a car:

```bash
python3 -m code.cli add-car --car-id CAR-101
```

Create a race:

```bash
python3 -m code.cli create-race --race-id RACE-1 --driver Ava --car CAR-101
```

Important note for beginners: each CLI command starts a fresh in-memory process.
That means state does not persist automatically between separate CLI commands.
Use tests for full end-to-end workflow validation.

### 4.4 Run all integration tests

```bash
cd rollnumber/integration
python3 -m pytest tests -q
```

Expected result: tests pass summary at the end (for example `X passed`).

### 4.5 Run one integration test file

```bash
cd rollnumber/integration
python3 -m pytest tests/test_integration_workflows.py -q
```

### 4.6 Run one single integration test case

```bash
cd rollnumber/integration
python3 -m pytest tests/test_integration_workflows.py::test_register_driver_then_enter_race_success -q
```

### 4.7 Run integration coverage (optional but recommended)

```bash
cd rollnumber/integration
python3 -m pytest tests --cov=code --cov-branch --cov-report=term-missing
```

### 4.8 If something fails (quick troubleshooting)

Make sure virtual environment is active (if you created one):

```bash
cd rollnumber
source .venv/bin/activate
```

Check required packages:

```bash
python3 -m pip show pytest pytest-cov
```

Re-run tests with full output:

```bash
cd rollnumber/integration
python3 -m pytest tests -vv
```

## 5. Blackbox (QuickCart API + Docker)

Blackbox tests require a running QuickCart backend API.

### 5.1 Start the QuickCart API with Docker (using provided `.tar`)

Run from the repository root:

```bash
cd rollnumber
docker load -i quickcart_image_x86.tar
docker images
```

Start container (replace `<IMAGE_NAME_OR_ID>` with the loaded image from `docker images`):

```bash
docker run -d --name quickcart-api -p 8000:8000 <IMAGE_NAME_OR_ID>
```

If a container with the same name already exists:

```bash
docker rm -f quickcart-api
docker run -d --name quickcart-api -p 8000:8000 <IMAGE_NAME_OR_ID>
```

### 5.2 Verify API is running before tests

```bash
docker ps --filter name=quickcart-api
docker logs --tail 50 quickcart-api
```

Quick API check (expected: `200 OK` + JSON response body):

```bash
curl -i "http://localhost:8000/api/v1/products" \
  -H "X-Roll-Number: 2024101105" \
  -H "X-User-ID: 1"
```

### 5.3 Set blackbox test environment variables

```bash
export QUICKCART_BASE_URL="http://localhost:8000/api/v1"
export QUICKCART_ROLL_NUMBER="2024101105"
export QUICKCART_USER_ID="1"
```

### 5.4 Run blackbox tests

Run full blackbox suite:

```bash
cd rollnumber/blackbox
python3 -m pytest tests -q
```

Run a single file:

```bash
cd rollnumber/blackbox
python3 -m pytest tests/test_cart_checkout_orders_initial.py -q
```

Run a single test case:

```bash
cd rollnumber/blackbox
python3 -m pytest tests/test_cart_checkout_orders_initial.py::test_checkout_card_success -q
```

### 5.5 Check results and troubleshoot quickly

If tests fail due to API not reachable:

```bash
curl -i "http://localhost:8000/api/v1/products" \
  -H "X-Roll-Number: 2024101105" \
  -H "X-User-ID: 1"
docker logs --tail 200 quickcart-api
```

If tests fail due to wrong headers, verify:

```bash
echo "$QUICKCART_BASE_URL"
echo "$QUICKCART_ROLL_NUMBER"
echo "$QUICKCART_USER_ID"
```

### 5.6 Stop/cleanup Docker container after testing

```bash
docker stop quickcart-api
docker rm quickcart-api
```

## 6. Reports

- `whitebox/report.md` and `whitebox/report.pdf`
- `integration/report.md` and `integration/report.pdf`
- `blackbox/report.md` and `blackbox/report.pdf`
