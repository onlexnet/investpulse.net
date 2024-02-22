from dataclasses import asdict, dataclass
from datetime import date
import os
from typing import Any, List

import pandas
from pandas import DataFrame

from .YahooFinance import LoadContext, YahooFinanceData, load

from .MarketAgent import MarketAgent, OrderExecuted
from .Strategy import ComputeStrategy1, ComputeStrategyState

folder_path = "test"
files = os.listdir(folder_path)

def run_test(asset_name: str, date_from: date, date_to: date):
    result_folder = '.data_result'
    os.makedirs(result_folder, exist_ok=True)  # create folder, if exists

    file_name_no_ext = f"{asset_name}-{date_from.strftime('%Y-%m-%d')}_{date_to.strftime('%Y-%m-%d')}"


    initial_budget = 2_500
    agent = MarketAgent(initial_budget)
    initial_state = ComputeStrategyState()
    strategy = ComputeStrategy1(initial_state, agent)
    ctx = LoadContext(date_from, date_to, asset_name)
    yahoo_data = load(ctx)
    
    orders: List[Any] = []
    def adjust_budget(event: OrderExecuted) -> None:
        event_asdict = asdict(event)
        orders.append(event_asdict)
    
    agent.add_listener(adjust_budget)
    
    for index, row in yahoo_data.iterrows():
        now64 = row['date']
        now = pandas.to_datetime(now64)
        close = row['close']
        finance_data = YahooFinanceData(now, 0, 0, 0, close, 0, 0)
        strategy.apply(finance_data)
        
    # Operations to CSV
    report = DataFrame(orders)
    file_path = os.path.join(result_folder, file_name_no_ext + ".details.csv")
    report.to_csv(file_path)

    # aggregated info. We reuse latest row fro mdata to get latest price
    @dataclass
    class FinalReport:
        initial_budget: float
        assets_number: float
        assets_value: float
        budget: float
        final_money: float
    close_price = row['close']
    assets_left_number = strategy._state.volume
    assets_left_value = round(close_price * assets_left_number, 2)
    final_budget = round(agent._budget, 2)
    final_money = round(final_budget + assets_left_value, 2)
    final_report = FinalReport(initial_budget, assets_left_number, assets_left_value, final_budget, final_money)

    # Final report    
    final_report_as_dict = asdict(final_report)
    report2 = DataFrame([final_report_as_dict])
    file_path = os.path.join(result_folder, file_name_no_ext + ".result.csv")
    report2.to_csv(file_path)


def test_performance():
    date_from = date(2019, 1, 1)
    date_to = date(2023, 12 ,31)

    run_test('msft', date_from, date_to)
        
