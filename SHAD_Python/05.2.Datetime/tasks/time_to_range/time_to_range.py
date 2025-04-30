import datetime
import enum
import typing as tp  # noqa


class GranularityEnum(enum.Enum):
    """
    Enum for describing granularity
    """
    DAY: datetime.timedelta = datetime.timedelta(days=1)
    TWELVE_HOURS: datetime.timedelta = datetime.timedelta(hours=12)
    HOUR: datetime.timedelta = datetime.timedelta(hours=1)
    THIRTY_MIN: datetime.timedelta = datetime.timedelta(minutes=30)
    FIVE_MIN: datetime.timedelta = datetime.timedelta(minutes=5)


def truncate_to_granularity(dt: datetime.datetime, gtd: GranularityEnum) -> datetime.datetime:
    """
    :param dt: datetime to truncate
    :param gtd: granularity
    :return: resulted datetime
    """
    match gtd:
        case GranularityEnum.DAY:
            return datetime.datetime(year=dt.year, month=dt.month, day=dt.day)
        case GranularityEnum.TWELVE_HOURS:
            return datetime.datetime(year=dt.year, month=dt.month, day=dt.day, hour=dt.hour // 12 * 12)
        case GranularityEnum.HOUR:
            return datetime.datetime(year=dt.year, month=dt.month, day=dt.day, hour=dt.hour)
        case GranularityEnum.THIRTY_MIN:
            return datetime.datetime(year=dt.year, month=dt.month, day=dt.day, hour=dt.hour,
                                     minute=dt.minute // 30 * 30)
        case _:
            return datetime.datetime(year=dt.year, month=dt.month, day=dt.day, hour=dt.hour, minute=dt.minute // 5 * 5)


class DtRange:
    def __init__(
            self,
            before: int,
            after: int,
            shift: int,
            gtd: GranularityEnum
    ) -> None:
        """
        :param before: number of datetimes should take before `given datetime`
        :param after: number of datetimes should take after `given datetime`
        :param shift: shift of `given datetime`
        :param gtd: granularity
        """
        self.__before: int = before
        self.__after: int = after
        self.__shift: int = shift
        self.__gtd: GranularityEnum = gtd

    def __call__(self, dt: datetime.datetime) -> list[datetime.datetime]:
        """
        :param dt: given datetime
        :return: list of datetimes in range
        """
        result: list[datetime.datetime] = []
        for i in range(-self.__before, self.__after + 1):
            result.append(truncate_to_granularity(dt + self.__gtd.value * (i + self.__shift), self.__gtd))
        return result


def get_interval(
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        gtd: GranularityEnum
) -> list[datetime.datetime]:
    """
    :param start_time: start of interval
    :param end_time: end of interval
    :param gtd: granularity
    :return: list of datetimes according to granularity
    """
    result: list[datetime.datetime] = []
    current_time: datetime.datetime = x if (x := truncate_to_granularity(start_time,
                                                                         gtd)) >= start_time else x + gtd.value
    while current_time <= end_time:
        result.append(current_time)
        current_time += gtd.value
    return result
