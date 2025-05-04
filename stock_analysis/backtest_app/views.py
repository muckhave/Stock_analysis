from django.shortcuts import render
from .forms import BacktestForm
from .models import BacktestResult
from backtesting import Backtest
from .strategies import RSIMACDStrategy, SmaCross, BollingerBandStrategy
from .utils import get_stock_data

def index(request):
    if request.method == "POST":
        form = BacktestForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data["ticker"]
            strategy_name = form.cleaned_data["strategy"]

            # 戦略クラスを選択
            strategy_class = {
                "RSIMACDStrategy": RSIMACDStrategy,
                "SmaCross": SmaCross,
                "BollingerBandStrategy": BollingerBandStrategy,
            }[strategy_name]

            # データ取得とバックテスト実行
            df = get_stock_data(ticker)
            bt = Backtest(df, strategy_class, cash=100000, trade_on_close=True)
            result = bt.run()

            # 結果を保存
            BacktestResult.objects.create(
                ticker=ticker,
                strategy_name=strategy_name,
                return_percentage=result["Return [%]"],
                trade_count=result["# Trades"],
                best_params=result._strategy.__dict__,
            )

            # 結果をテンプレートに渡す
            return render(request, "backtest_app/results.html", {"result": result})

    else:
        form = BacktestForm()

    return render(request, "backtest_app/index.html", {"form": form})
