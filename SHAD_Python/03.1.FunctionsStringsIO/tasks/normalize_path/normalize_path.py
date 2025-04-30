def normalize_path(path: str) -> str:
    """
    :param path: unix path to normalize
    :return: normalized path
    """
    if not path or path == '.':
        return '.'

    direct: list[str] = []
    absolute = path.startswith('/')

    for part in path.split('/'):
        if part in ('', '.'):
            continue
        elif part == '..':
            if direct and direct[-1] != '..':
                direct.pop()
            elif not absolute:
                direct.append('..')
        else:
            direct.append(part)

    normalized_path = '/'.join(direct)
    return '/' + normalized_path if absolute else normalized_path or '.'
