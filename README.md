
# 🏗️ Magazyn360

Magazyn360 is a modern SaaS ERP system designed to support the management of small and medium-sized enterprises. The project features full automation of deployment processes using CI/CD, application containerization with Docker, and orchestration with Kubernetes (K8s).

[![CI](https://github.com/aleksanderbialka/magazyn360/actions/workflows/main_magazyn360.yml/badge.svg)](https://github.com/aleksanderbialka/magazyn360)
[![CI](https://github.com/aleksanderbialka/bioscopeai-core/actions/workflows/main_bioscopeai_core.yml/badge.svg)](https://github.com/aleksanderbialka/bioscopeai-core)

---

## 📦 Technology Stack

- **Backend**: Python, Django, Django REST Framework
- **Database**: PostgreSQL
- **API**: REST + Swagger
- **Frontend**: Angular** (TODO)
- **CI/CD**: GitHub Actions
- **Containerization**: Docker
- **Image Registry**: Github Registry Containers
- **Kubernetes**: K8s
- **Helm**: Helm Chart for deployment management
- **Error Monitoring**: Sentry
- **Testing**: pytest + coverage + pytest-html

---

## 🚀 Quick Local Start

```bash
# 1. Clone the repository
git clone https://github.com/your-user/magazyn360.git
cd magazyn360

# 2. Run the service locally with Docker Compose
docker-compose up --build
```

---

## 🔄 CI/CD Workflow

Main steps of the CI/CD pipeline (`.github/workflows/main.yml`):

1. **Linting** – using Ruff and Black
2. **Build & Test** – container build + unit tests
3. **Push** – publish image to GHCR Artifactory
4. **Deploy** – install/update on AKS via Helm

To trigger the pipeline manually:

```bash
GitHub → Actions → Magazyn360 CI/CD -- MAIN workflow
```

---

## ⚙️ Deployment on K8s (Kubernetes)

We use a Helm Chart with the following files:

```
helm-chart/
├── Chart.yaml

├── values.yaml
├── secrets.yaml (base64 in GitHub Secrets)
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    └── secrets.yaml
```

Example local deployment:

```bash
helm upgrade --install magazyn360 ./helm-chart -n magazyn360 --create-namespace \
  -f helm-chart/values.yaml \
  -f helm-chart/secrets.yaml
```

---

## 🔑 Secrets and Configuration

- AKS kubeconfig stored as `KUBECONFIG_BASE64`
- `secrets.yaml` file stored as `HELM_SECRETS_YAML2`
- GHCR credentials in GitHub Secrets:
  - `GITHUB_TOKEN`

---

## 🧪 Testing

```bash
# Run tests with HTML report:
poetry run pytest --junitxml=results/pytest-results.xml --html=results/pytest-report.html
```

Reports appear as artifacts in GitHub Actions.

---

## 📂 Directory Structure

```
magazyn360/
├── magazyn360-api/           # Django API
│   ├── apps/core/            # Models: User, Company, Address
│   ├── apps/warehouse/       # Models: Warehouse, Product, Stock, WarehouseDocument, WarehouseDocumentItem
│   ├── bin/run_tests.sh      # Test runner script
│   └── ...
├── helm-chart/               # Helm Chart
├── .github/workflows/        # GitHub Actions workflow files
├── docker-compose.yml
└── README.md
```

---
