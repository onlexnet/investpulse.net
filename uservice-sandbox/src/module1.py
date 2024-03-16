import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import accuracy_score


def hello1() -> str:
    return 'Hello'

def load_data() -> GradientBoostingRegressor:
    # Wczytanie danych z pliku CSV
    data = pd.read_csv('MSFT_data_2019-02-15_2024-02-14.csv')

    # # Usunięcie kolumny Date, jeśli nie jest potrzebna do modelowania
    data = data.drop('Date', axis=1)

    # # Podział danych na cechy (features) i etykiety (labels)
    X = data.drop('Close', axis=1)
    y = data['Close']

    # # Podział danych na zbiory treningowy i testowy
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # # Inicjalizacja modelu Gradient Boosting Regressor
    model = GradientBoostingRegressor()

    # # Trenowanie modelu na danych treningowych
    model.fit(X_train, y_train)

    # # Sprawdzenie dokładności modelu na danych testowych
    # accuracy = model.score(X_test, y_test)
    # return f"Dokładność modelu: {accuracy}"
    return model
