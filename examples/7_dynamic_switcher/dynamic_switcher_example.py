import asyncio
from lightweight_charts import Chart

CRYPTOS = ('BTCUSDT', 'ETHUSDT')
COINS = ('EURUSD', 'GBPUSD')

def on_instrument_selection(chart):
    selected =chart.topbar["instrument"].value
    if selected == "Crypto":
        chart.topbar.switcher(
                name='pair',
                options=CRYPTOS,
                default=CRYPTOS[0],
                func=on_pair_selection)
    else:
        chart.topbar.switcher(
                name='pair',
                options=COINS,
                default=COINS[0],
                func=on_pair_selection)
    #
    print(f'Using to {chart.topbar["instrument"].value}')

def on_pair_selection(chart):
    print(f'Trading {chart.topbar["pair"].value}')


async def main():
    chart = Chart(debug=False)
    chart.topbar.switcher(
            name='instrument',
            options=('Crypto', 'Currency'),
            default='Crypto',
            func=on_instrument_selection)

    chart.topbar.switcher(
            name='pair',
            options=CRYPTOS,
            default=CRYPTOS[0],
            func=on_pair_selection)
    
    chart.topbar.textbox('info')
    chart.topbar['info'].set('DYNAMIC SWITCHER')

    #    chart.show(block=True)
    await chart.show_async(block=True)


if __name__ == '__main__':
    asyncio.run(main())
