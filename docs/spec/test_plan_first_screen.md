# Test Plan: Ekran główny (Ranking akcji/ETF)

## Cel
Zweryfikować poprawność działania ekranu głównego rankingu akcji/ETF-ów na podstawie rzeczywistych danych z backendu.

## Zakres testów
- Prezentacja danych (symbol, nazwa, AI score, zwrot 1M, trend, kraj/kategoria)
- Interakcje UI (wyszukiwanie, przełączanie sekcji, paginacja)
- Obsługa błędów i stanów brzegowych
- Responsywność i dostępność

## Scenariusze testowe
1. **Wyświetlenie listy akcji/ETF**
   - Po uruchomieniu aplikacji wyświetla się lista z danymi pobranymi z backendu
2. **Poprawność danych**
   - Każdy wiersz zawiera symbol, nazwę, AI score (kolor), zwrot 1M (kolor), trend (ikona), kraj/kategoria (badge)
3. **Wyszukiwanie**
   - Wpisanie frazy w pole wyszukiwania filtruje listę po symbolu/nazwie
4. **Paginacja/przełączanie sekcji**
   - Przycisk "Show ETFs" przełącza widok na ETF-y
   - Przycisk "Show More" ładuje kolejne pozycje
5. **Obsługa błędów**
   - W przypadku braku danych lub błędu API wyświetla się komunikat o błędzie
6. **Responsywność**
   - Layout poprawnie wyświetla się na desktopie i mobile
7. **Dostępność**
   - Wszystkie elementy są dostępne z klawiatury, mają poprawne role ARIA

## Automatyzacja
- Testy E2E (np. Playwright/Cypress) uruchamiane lokalnie i w CI na deweloperskiej wersji platformy
- Testy snapshotów UI (np. Storybook, React Testing Library)
- Testy integracyjne API (mock backend lub staging)

## Uwagi
- Testy powinny być powiązane z rzeczywistymi danymi testowymi z backendu
- Scenariusze mogą być rozszerzane wraz z rozwojem funkcjonalności
