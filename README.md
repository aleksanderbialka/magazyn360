
# 🏗️ Magazyn360

Magazyn360 to nowoczesny system ERP typu SaaS wspomagający zarządzanie składami budowlanymi. Projekt zakłada pełną automatyzację procesów wdrożeniowych z wykorzystaniem CI/CD, konteneryzację aplikacji w Dockerze oraz orkiestrację za pomocą Kubernetes (AKS).

---

## 📦 Stack technologiczny

- **Backend**: Python, Django, Django REST Framework
- **Baza danych**: PostgreSQL
- **API**: REST + Swagger (drf-spectacular)
- **Frontend**: (docelowo) React
- **CI/CD**: GitHub Actions
- **Konteneryzacja**: Docker
- **Rejestr obrazów**: JFrog Artifactory
- **Kubernetes**: AKS (Azure Kubernetes Service)
- **Helm**: Helm Chart do zarządzania wdrożeniami
- **Monitorowanie błędów**: Sentry
- **Testy**: pytest + coverage + pytest-html

---

## 🚀 Szybki start lokalnie

```bash
# 1. Klonuj repozytorium
git clone https://github.com/your-user/magazyn360.git
cd magazyn360

# 2. Uruchom usługę lokalnie z Docker Compose
docker-compose up --build
```

---

## 🔄 CI/CD Workflow

Główne kroki pipeline’u CI/CD (`.github/workflows/main.yml`):

1. **Linting** – z użyciem Ruff i Black
2. **Build & Test** – budowa kontenera + testy jednostkowe
3. **Push** – publikacja obrazu do JFrog Artifactory
4. **Deploy** – instalacja/aktualizacja na AKS przez Helm

Aby uruchomić pipeline ręcznie:

```bash
GitHub → Actions → Magazyn360 CI/CD -- MAIN workflow
```

---

## ⚙️ Deployment na AKS (Kubernetes)

Używamy Helm Charta z plikami:

```
helm-chart/
├── Chart.yaml
├── values.yaml
├── secrets.yaml (base64 w GitHub Secrets)
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    └── secrets.yaml
```

Przykład lokalnego deploya:

```bash
helm upgrade --install magazyn360 ./helm-chart -n magazyn360 --create-namespace \
  -f helm-chart/values.yaml \
  -f helm-chart/secrets.yaml
```

---

## 🔑 Sekrety i konfiguracja

- Kubeconfig do AKS przechowywany jako `KUBECONFIG_BASE64`
- Plik `secrets.yaml` trzymany jako `HELM_SECRETS_YAML2`
- Dane logowania do JFrog w GitHub Secrets:
  - `JFROG_REGISTRY`
  - `JFROG_REPO`
  - `JFROG_USERNAME`
  - `JFROG_PASSWORD`

---

## 🧪 Testowanie

```bash
# Uruchomienie testów z raportem HTML:
poetry run pytest --junitxml=results/pytest-results.xml --html=results/pytest-report.html
```

Raporty pojawiają się jako artefakty w GitHub Actions.

---

## 📂 Struktura katalogów

```
magazyn360/
├── magazyn360-api/           # Django API
│   ├── apps/core/            # Modele: User, Company, Address
│   ├── bin/run_tests.sh      # Skrypt do uruchamiania testów
│   └── ...
├── helm-chart/               # Helm Chart
├── .github/workflows/        # Pliki workflow GitHub Actions
├── docker-compose.yml
└── README.md
```

---
