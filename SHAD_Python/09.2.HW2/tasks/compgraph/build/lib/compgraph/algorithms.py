import math
import typing as tp
from collections import Counter
from datetime import datetime

from . import Graph, operations

TRow = dict[str, tp.Any]
TRowsIterable = tp.Iterable[TRow]


def word_count_graph(input_stream_name: str, text_column: str = "text", count_column: str = "count") -> Graph:
    """Constructs graph which counts words in text_column of all rows passed"""
    return Graph.graph_from_iter(input_stream_name) \
        .map(operations.FilterPunctuation(text_column)) \
        .map(operations.LowerCase(text_column)) \
        .map(operations.Split(text_column)) \
        .sort([text_column]) \
        .reduce(operations.Count(count_column), [text_column]) \
        .sort([count_column, text_column])


def inverted_index_graph(input_stream_name: str, doc_column: str = "doc_id", text_column: str = "text",
                         result_column: str = "tf_idf") -> Graph:
    """Constructs graph which calculates td-idf for every word/document pair"""
    splt = Graph.graph_from_iter(input_stream_name) \
        .map(operations.FilterPunctuation(text_column)) \
        .map(operations.LowerCase(text_column)) \
        .map(operations.Split(text_column))
    count_docs = Graph.graph_from_iter(input_stream_name) \
        .map(operations.FilterPunctuation(text_column)) \
        .map(operations.LowerCase(text_column)) \
        .reduce(operations.CountRows(doc_column), [])
    count_idf = splt.sort([doc_column, text_column]) \
        .reduce(operations.First(text_column), [doc_column, text_column]) \
        .sort([text_column]) \
        .reduce(operations.CountRows(text_column, "docw_count"), [text_column]) \
        .join(operations.InnerJoiner(), count_docs, []) \
        .map(operations.Divide()) \
        .map(operations.Evaluate(lambda row: {**row, "IDF": math.log(row["IDF"])}))
    tf = Graph.graph_from_iter(input_stream_name) \
        .map(operations.FilterPunctuation(text_column)) \
        .map(operations.LowerCase(text_column)) \
        .map(operations.Split(text_column)) \
        .sort([doc_column]) \
        .reduce(operations.TermFrequency(text_column, "TF"), [doc_column])
    return tf.sort([text_column]) \
        .join(operations.OuterJoiner(), count_idf, [text_column]) \
        .map(operations.Product(("TF", "IDF"), result_column)) \
        .map(operations.Del(("TF", "IDF"))) \
        .reduce(operations.TopN(result_column, 3), [text_column])


def add_word_count(rows: TRowsIterable, text_column: str = "text_column"):
    """
    Adds a word count column to each row based on the frequency of the text in the specified column.
    """
    counter = Counter(row[text_column] for row in rows)
    for row in rows:
        yield {**row, "word_count": counter[row[text_column]]}


def pmi_graph(input_stream_name: str, doc_column: str = "doc_id", text_column: str = "text",
              result_column: str = "pmi") -> Graph:
    """Constructs graph which gives for every document the top 10 words ranked by pointwise mutual information"""
    cond = Graph.graph_from_iter(input_stream_name) \
        .map(operations.FilterPunctuation(text_column)) \
        .map(operations.LowerCase(text_column)) \
        .map(operations.Split(text_column)) \
        .map(operations.Filter(lambda x: len(x[text_column]) > 3)) \
        .sort([doc_column]) \
        .reduce(operations.UniversalReducer(lambda rows: add_word_count(rows, text_column=text_column)), [doc_column]) \
        .map(operations.Filter(lambda x: x["word_count"] > 1))
    tf_in_doci = cond.copy() \
        .sort([doc_column]) \
        .reduce(operations.TermFrequency(text_column, "tf_in_doci"), [doc_column]) \
        .sort([text_column])
    return cond.reduce(operations.TermFrequency(text_column), []) \
        .sort([text_column]) \
        .join(operations.InnerJoiner(), tf_in_doci, [text_column]) \
        .map(operations.Divide("tf_in_doci", "tf", result_column)) \
        .map(operations.Evaluate(lambda row: {**row, result_column: math.log(row[result_column])})) \
        .sort([doc_column]) \
        .reduce(operations.TopN(result_column, 10, True), [doc_column])


def dist(row: TRow, start: str = "start", end: str = "end", length: str = "length", r: float = 6373) -> TRow:
    """
    Calculates the great-circle distance between two points and adds the result to the row.
    """
    start1, end1 = math.radians(row[start][0]), math.radians(row[end][0])
    start2, end2 = math.radians(row[start][1]), math.radians(row[end][1])
    new_row = row.copy()
    new_row[length] = \
        (2 * r *
         math.asin(
             math.sqrt(
                 math.sin((end2 - start2) / 2) ** 2 +
                 math.cos(start2) *
                 math.cos(end2) *
                 math.sin(
                     (end1 - start1) / 2) ** 2
             )
         )
         )
    return new_row


def dis_iso(row: TRow, start: str = "enter_time", end: str = "leave_time", format_str: str = "%Y%m%dT%H%M%S.%f",
            weekday: str = "weekday", hour: str = "hour") -> TRow:
    """
    Computes the time difference in hours between two timestamps and adds weekday and hour fields to the row.
    """
    new_row = row.copy()
    if "." in row[start]:
        start_time = datetime.strptime(row[start], format_str)
    else:
        start_time = datetime.strptime(row[start], "%Y%m%dT%H%M%S")
    if "." in row[end]:
        end_time = datetime.strptime(row[end], format_str)
    else:
        end_time = datetime.strptime(row[end], "%Y%m%dT%H%M%S")
    new_row["time"] = (end_time - start_time).total_seconds() / 3600
    new_row[weekday] = start_time.strftime("%a")
    new_row[hour] = getattr(start_time, "hour")
    return new_row


def yandex_maps_graph(input_stream_name_time: str, input_stream_name_length: str,
                      enter_time_column: str = "enter_time", leave_time_column: str = "leave_time",
                      edge_id_column: str = "edge_id", start_coord_column: str = "start", end_coord_column: str = "end",
                      weekday_result_column: str = "weekday", hour_result_column: str = "hour",
                      speed_result_column: str = "speed") -> Graph:
    """Constructs graph which measures average speed in km/h depending on the weekday and hour"""
    length = Graph.graph_from_iter(input_stream_name_length).sort([edge_id_column])
    r = 6373
    return Graph.graph_from_iter(input_stream_name_time) \
        .sort([edge_id_column]) \
        .join(operations.InnerJoiner(), length, [edge_id_column]) \
        .map(operations.Filter(lambda row: row[enter_time_column] <= row[leave_time_column])) \
        .map(operations.Evaluate(lambda row: dist(row, start_coord_column, end_coord_column, "length", r))) \
        .map(operations.Evaluate(
        lambda row: dis_iso(row, enter_time_column, leave_time_column, "%Y%m%dT%H%M%S.%f",
                            weekday=weekday_result_column, hour=hour_result_column))) \
        .map(operations.Evaluate(lambda row: {**row, speed_result_column: row["length"] / (row["time"])})) \
        .map(operations.Project([weekday_result_column, hour_result_column, speed_result_column])) \
        .sort([weekday_result_column, hour_result_column]) \
        .reduce(operations.Mean(speed_result_column), [weekday_result_column, hour_result_column])
