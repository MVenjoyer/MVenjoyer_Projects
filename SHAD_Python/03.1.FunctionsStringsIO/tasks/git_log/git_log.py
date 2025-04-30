import typing as tp


def reformat_git_log(inp: tp.IO[str], out: tp.IO[str]) -> None:
    """Reads git log from `inp` stream, reformats it and prints to `out` stream

    Expected input format: `<sha-1>\t<date>\t<author>\t<email>\t<message>`
    Output format: `<first 7 symbols of sha-1>.....<message>`
    """
    for line in inp:
        sha, _, _, _, message = line.split("\t", maxsplit=4)
        out.write(f"{sha[:7]}" + "." * (80 - 7 - len(message) + 1) + f"{message}")
