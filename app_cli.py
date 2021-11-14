import download
from connection_pool import get_connection
import database


MAIN_MENU_PROMPT = """
--- Main Menu ---

1) Update price data (bars)
2) Update single ticker price data
3) Menu 3
q) Exit Main Menu

Enter your choise:"""

# --- Menu Prompts ---


def update_bars_promt():
    exchange = input('Enter Exchange (Oslo, Sp500, Stockholm):')
    period = input('Enter period (1y, 2y...):')
    max_tickers = input('Enter max tickers to update:')

    max_tickers = 999 if max_tickers == '' else int(max_tickers)
    update_bars(exchange, period, max_tickers)


def update_ticker_prompt():
    ticker = input('Enter ticker:')
    period = input('Enter period (1y, 2y...):')
    update_ticker(ticker=ticker, period=period)


def menu_3():
    print('Menu 3')

# --- Menu Functions ---


def update_ticker(ticker, period):
    print(f"Update {ticker} for period of {period}")
    df = download.download_history(ticker, period)
    df = download.filter_data_by_ts(df, ticker)
    bulk_insert(df, 'bars')


def update_bars(exchange, period, max_tickers):
    print(f"Update {exchange} for period of {period}")
    # Get list of tickers
    with get_connection() as connection:
        tickers = database.get_tickers(connection, exchange, max_tickers)

    # loop ticker list
    for ticker in tickers:
        # bulk insert for each ticker
        update_ticker(ticker[0], period)


def bulk_insert(df, table):
    if len(df) > 0:
        with get_connection() as connection:
            ret = database.bulk_insert_bars(connection, df, table)
            if ret is True:
                print(f"Inserted {len(df)} rows!")
            else:
                print(ret)
    else:
        print('Nothing to insert!')


MAIN_MENU_OPTIONS = {
    '1': update_bars_promt,
    '2': update_ticker_prompt,
    '3': menu_3
}


def main_menu():
    while (selection := input(MAIN_MENU_PROMPT)) != 'q':
        try:
            MAIN_MENU_OPTIONS[selection]()
        except KeyError:
            print('Invalid Input Selection. Please trye again!')


if __name__ == '__main__':
    main_menu()
