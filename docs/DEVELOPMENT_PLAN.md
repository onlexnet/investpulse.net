# Development Plan: Predictive Trading Dashboard (Danelfin.com Clone)

## Cel projektu
Stworzenie aplikacji webowej inspirowanej Danelfin.com, która prezentuje ranking akcji/ETF-ów na podstawie rzeczywistych danych rynkowych oraz prostych analiz statystycznych. Docelowo frontend (webapp) będzie korzystał z backendu udostępniającego aktualne dane i wyniki obliczeń.

---

## Etapy realizacji

### 1. Pozyskanie i przygotowanie danych
- **Źródła danych:**
  - [Yahoo Finance API](https://finance.yahoo.com/lookup) (np. przez bibliotekę yfinance dla Pythona)
  - [Alpha Vantage](https://www.alphavantage.co/) (darmowe API, limity)
  - [Polygon.io](https://polygon.io/) (płatne, szeroki zakres danych)
  - [Stooq.pl](https://stooq.pl/) (dane giełdowe, CSV)
- **Zakres danych:**
  - Notowania akcji/ETF (symbol, nazwa, kurs, zmiana, wolumen, kraj, sektor)
  - Historyczne ceny (do wyliczeń zwrotów, zmienności, itp.)
  - Dodatkowe: AI score (na początek losowy lub prosty algorytm)

### 2. Backend (API)
- **Technologia:** Python (FastAPI lub Flask)
- **Funkcjonalności:**
  - Endpoint do pobierania listy akcji/ETF z podstawowymi danymi
  - Endpoint do pobierania szczegółów wybranego instrumentu
  - Endpoint do pobierania danych historycznych (np. do wykresów)
  - Proste wyliczenia: zwroty 1M/3M/1Y, zmienność, ranking wg wybranej metryki
  - (Opcjonalnie) Endpoint do generowania/proxy AI score
- **Przykład:**
  - `GET /api/stocks` → lista akcji/ETF
  - `GET /api/stocks/{symbol}` → szczegóły
  - `GET /api/stocks/{symbol}/history` → dane historyczne

### 3. Integracja backendu z frontendem
- **Zmiana źródła danych w webapp:**
  - Zastąpienie danych dummy w `PopularStocksRanking.tsx` danymi z API
  - Obsługa ładowania, błędów, fallbacków
  - Typowanie odpowiedzi API (TypeScript interfaces)

### 4. Rozbudowa prezentacji i analityki
- **Nowe sekcje:**
  - Wykresy historyczne (np. Chart.js, recharts)
  - Szczegółowe karty instrumentów
  - Filtrowanie, sortowanie, wyszukiwanie
- **Dodatkowe metryki:**
  - Średnia zmienność, Sharpe ratio, proste wskaźniki techniczne

### 5. Testy i automatyzacja
- **Testy backendu:**
  - Testy endpointów (np. pytest, unittest, supertest)
- **Testy frontendu:**
  - Testy komponentów (React Testing Library)
- **Automatyzacja:**
  - Skrypty do pobierania i aktualizacji danych
  - CI/CD (GitHub Actions)

---

## Proponowana kolejność prac
1. Wybór i test źródła danych (np. yfinance, Alpha Vantage)
2. Prototyp backendu: pobieranie i serwowanie danych przez REST API
3. Podmiana danych dummy w webapp na dane z backendu
4. Dodanie prostych wyliczeń i rankingów po stronie backendu
5. Rozbudowa UI o nowe sekcje i metryki
6. Testy i automatyzacja

---


## Kluczowe pliki i foldery
- `webapp/` – frontend Next.js (główna logika: `src/components/PopularStocksRanking.tsx`)
- `try/` – backend (serwis API w Pythonie: FastAPI lub Flask)
- `infra/` – provisioning środowiska (opcjonalnie Docker, Terraform)

---

## Deployment i środowiska testowe

- **Platforma docelowa:** Azure (Microsoft Cloud)
- **Optymalizacja kosztów:**
  - Wybór najtańszych usług (np. Azure App Service Free, Azure Container Apps, Azure Functions Consumption Plan, Azure Storage Account, darmowe bazy danych)
  - Automatyczne wyłączanie nieużywanych środowisk testowych
  - Monitoring kosztów i alerty budżetowe
- **Testowanie i CI:**
  - Każdy pull request i commit uruchamia testy na środowisku testowym w Azure (np. GitHub Actions + Azure CLI)
  - Możliwość uruchamiania backendu i frontendu lokalnie z symulacją środowiska Azure (np. Azurite, lokalne kontenery)
  - Dokumentacja deploymentu i testów w `infra/` oraz w dedykowanych plikach README

---

**Uwaga:** Folder `try/` jest ignorowany przez Copilota, ale backend należy rozwijać zgodnie z powyższym planem (manualnie lub przez dedykowane narzędzia backendowe).

---

Po akceptacji planu można rozbić zadania na szczegółowe issues/tickety.
