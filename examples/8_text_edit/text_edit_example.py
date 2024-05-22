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

def on_info2_input(chart):
    print(f'info2 {chart.topbar["info2"].value}')

async def main():
    chart = Chart(debug=True)
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
    
    #chart.topbar.textbox(name='info1', initial_text='DYNAMIC SWITCHER')
    chart.topbar.textbox(name='info1')
    chart.topbar['info1'].set('DYNAMIC SWITCHER')

    chart.topbar.textbox(
            name='info2',
             initial_text="test",
             label="INFOX",
             func=on_info2_input)

    await chart.show_async(block=True)


if __name__ == '__main__':
    asyncio.run(main())
