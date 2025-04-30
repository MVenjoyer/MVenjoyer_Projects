import typing as tp

import pandas as pd


def male_age(df: pd.DataFrame) -> float:
    """
    Return mean age of survived men, embarked in Southampton with fare > 30
    :param df: dataframe
    :return: mean age
    """
    return df[(df['Survived'] == 1) & (df['Sex'] == 'male') & (df['Embarked'] == 'S') & (df['Fare'] > 30)]['Age'].mean()


def nan_columns(df: pd.DataFrame) -> tp.Iterable[str]:
    """
    Return list of columns containing nans
    :param df: dataframe
    :return: series of columns
    """
    return df.columns[df.isnull().any()].tolist()


def class_distribution(df: pd.DataFrame) -> pd.Series:
    """
    Return Pclass distrubution
    :param df: dataframe
    :return: series with ratios
    """
    return df['Pclass'].value_counts(normalize=True)


def families_count(df: pd.DataFrame, k: int) -> int:
    """
    Compute number of families with more than k members
    :param df: dataframe,
    :param k: number of members,
    :return: number of families
    """
    df['Surname'] = df['Name'].str.split(',').str[0]
    family_counts = df['Surname'].value_counts()
    return (family_counts > k).sum()


def mean_price(df: pd.DataFrame, tickets: tp.Iterable[str]) -> float:
    """
    Return mean price for specific tickets list
    :param df: dataframe,
    :param tickets: list of tickets,
    :return: mean fare for this tickets
    """
    return df[df['Ticket'].isin(tickets)]['Fare'].mean()


def max_size_group(df: pd.DataFrame, columns: list[str]) -> tp.Iterable[tp.Any]:
    """
    For given set of columns compute most common combination of values of these columns
    :param df: dataframe,
    :param columns: columns for grouping,
    :return: list of most common combination
    """
    return df.groupby(columns).size().idxmax()


def is_lucky(ticket: str) -> bool:
    if not ticket.isdigit():
        return False
    if (length := len(ticket)) % 2 != 0:
        return False
    return sum(int(digit) for digit in ticket[:length // 2]) == sum(int(digit) for digit in ticket[length // 2:])


def dead_lucky(df: pd.DataFrame) -> float:
    """
    Compute dead ratio of passengers with lucky tickets.
    A ticket is considered lucky when it contains an even number of digits in it
    and the sum of the first half of digits equals the sum of the second part of digits
    ex:
    lucky: 123222, 2671, 935755
    not lucky: 123456, 62869, 568290
    :param df: dataframe,
    :return: ratio of dead lucky passengers
    """
    df['IsLucky'] = df['Ticket'].apply(is_lucky)
    if (lucky_passengers := df[df['IsLucky']]).empty:
        return 0.0
    return lucky_passengers['Survived'].value_counts().get(0, 0) / lucky_passengers.shape[0]
