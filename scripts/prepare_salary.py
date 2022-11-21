import argparse
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd


def str_to_dict(value: str) -> Dict[str, str]:
    """
    Convert string to dict
    :param value: input string
    :return:
    """
    try:
        result = eval(value)
        if not isinstance(result, dict):
            raise ValueError('`value` is expected to be a dict expression')
        return result
    except TypeError:
        return value


def read_data(path: Path, usecols: Optional[Union[List[str], str]] = None) -> pd.DataFrame:
    if isinstance(usecols, str):
        usecols = [usecols]
    return pd.read_excel(path, usecols=usecols, engine='openpyxl')


def process(data: pd.DataFrame) -> pd.DataFrame:
    """
    Process salary

    :param data: dump of hh.ru
    :return: processed salary with same indices as in `data`
    """
    data = data.dropna()
    salary_decomposed = data['salary'].apply(lambda value: pd.Series(str_to_dict(value)))
    is_gross = salary_decomposed['gross'].fillna(True).replace({False: 1, True: 0.87})
    salary_decomposed['from'] = salary_decomposed['from'] * is_gross
    salary_decomposed['to'] = salary_decomposed['to'] * is_gross

    salary = salary_decomposed[['to', 'from']].mean(axis=1)
    usd_to_rub = 56.2996
    eur_to_rub = 57.921
    kzt_to_rub = 100/13.5040

    salary = salary.where(salary_decomposed['currency'] != 'USD', salary*usd_to_rub)
    salary = salary.where(salary_decomposed['currency'] != 'EUR', salary*eur_to_rub)
    salary = salary.where(salary_decomposed['currency'] != 'KZT', salary*kzt_to_rub)
    salary.name = 'salary'
    salary = salary.to_frame()
    salary.index.name = 'index'

    return salary


if __name__ == '__main__':

    # Create CLI arguments parser insttance
    parser = argparse.ArgumentParser(
        description='prepare_salary.py: extract salary column for input datable and return table with processed salary',
        epilog='Example of use: python prepare_salary.py -i "region roles (26.05.22).xlsx" -o salary.csv',
        prog='prepare_salary.py',
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Define arguments expected behavior
    parser.add_argument('-i', '--input', required=True, help='path to the hh.ru dump table')
    parser.add_argument('-o', '--output', required=False, default='salary.csv', help='path to the output file')

    # Get arguments from command line into Python objects as attributes of args
    args = parser.parse_args()

    data = read_data(path=args.input, usecols='salary')
    salary = process(data)

    salary.to_csv(args.output)














