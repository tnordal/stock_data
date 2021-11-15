import download
from connection_pool import get_connection
import database

import pandas as pd
pd.options.mode.chained_assignment = None

PATH_COMPANIES_FILES = 'data_files/companies/'

MAIN_MENU_PROMPT = """
--- Main Menu ---

1) Update price data (bars)
2) Update single ticker price data
3) Update Companies from csv file
4) Add a Companie
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


def update_companies_promt():
    print('Update companies from csv')
    csv_file = input('Enter name csv-file:')
    col_ticker = input('Enter column name for the ticker:')
    col_name = input('Enter column name for the companie name:')
    col_sector = input('Enter column name for the sector:')
    exchange = input('Enter exchange name:')
    print(
        f"update_companies({csv_file}, {col_ticker}, {col_name}, {col_sector})"
    )
    update_companies(
        ticker_file=csv_file,
        ticker_column=col_ticker,
        name_column=col_name,
        sector_column=col_sector,
        exchange=exchange
    )


def add_companie_promt():
    print('Add companie')
    ticker = input('Enter ticker:').upper()
    companie = input('Enter Companie name:')
    exchange = input('Enter Exchange name:')
    sector = input('Enter a Sector:')
    print(f"Add {companie} in sector {sector} with {ticker} as ticker")
    add_companie(ticker, companie, exchange, sector)

# --- Menu Functions ---


def update_ticker(ticker, period):
    print(f"Update {ticker} for period of {period}")
    df = download.download_history(ticker, period)
    df = download.filter_data_by_ts(df, ticker)
    # TODO Force volume column to int
    df.dropna(axis=0, inplace=True)
    df = df.astype({'volume': 'int32'}, copy=True)
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


def update_companies(
    ticker_file,
    ticker_column,
    name_column,
    sector_column,
    exchange
):
    ticker_file = PATH_COMPANIES_FILES + ticker_file
    df = download.prepare_companies_file_for_db(
        ticker_file=ticker_file,
        ticker_column=ticker_column,
        name_column=name_column,
        sector_column=sector_column,
        exchange=exchange
    )

    if len(df) > 0:
        with get_connection() as connection:
            ret = database.bulk_insert_bars(connection, df, 'companies')
            if ret is True:
                print(f"Inserted {len(df)} rows!")
            else:
                print(ret)
    else:
        print('Nothing to insert!')


def add_companie(ticker, name, exchange, sector):
    with get_connection() as connection:
        new_ticker = database.add_companie(
            connection=connection,
            ticker=ticker,
            name=name,
            exchange=exchange,
            sector=sector
        )
    if new_ticker:
        print(f"Ticker {new_ticker} added")
    else:
        print(f"Ticker {ticker} already exists in DB!")


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
    '3': update_companies_promt,
    '4': add_companie_promt
}


def main_menu():
    while (selection := input(MAIN_MENU_PROMPT)) != 'q':
        try:
            MAIN_MENU_OPTIONS[selection]()
        except KeyError:
            print('Invalid Input Selection. Please trye again!')


if __name__ == '__main__':
    main_menu()
