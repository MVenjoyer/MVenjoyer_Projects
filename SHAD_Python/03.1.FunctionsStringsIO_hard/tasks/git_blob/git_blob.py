import zlib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class BlobType(Enum):
    """Helper class for holding blob type"""
    COMMIT = b'commit'
    TREE = b'tree'
    DATA = b'blob'

    @classmethod
    def from_bytes(cls, type_: bytes) -> 'BlobType':
        for member in cls:
            if member.value == type_:
                return member
        assert False, f'Unknown type {type_.decode("utf-8")}'


@dataclass
class Blob:
    """Any blob holder"""
    type_: BlobType
    content: bytes


@dataclass
class Commit:
    """Commit blob holder"""
    tree_hash: str
    parents: list[str]
    author: str
    committer: str
    message: str


@dataclass
class Tree:
    """Tree blob holder"""
    children: dict[str, Blob]


def read_blob(path: Path) -> Blob:
    """
    Read blob-file, decompress and parse header
    :param path: path to blob-file
    :return: blob-file type and content
    """
    with open(path, 'rb') as file:
        data = zlib.decompress(file.read())
    return Blob(BlobType.from_bytes(data[:data.find(b' ')]), data[data.find(b'\x00') + 1:])


def traverse_objects(obj_dir: Path) -> dict[str, Blob]:
    """
    Traverse directory with git objects and load them
    :param obj_dir: path to git "objects" directory
    :return: mapping from hash to blob with every blob found
    """
    answer: dict[str, Blob] = {}
    for path in obj_dir.rglob('*'):
        if path.is_file():
            answer[path.parent.name[:2] + path.name] = read_blob(path)
    return answer


def parse_commit(blob: Blob) -> Commit:
    """
    Parse commit blob
    :param blob: blob with commit type
    :return: parsed commit
    """
    content = blob.content.decode().split('\n')
    tree_hash, parents, author, committer, message = "", [], "", "", ""
    for el in content:
        elements = el.split(" ", 1)
        if elements[0] == "tree":
            tree_hash = elements[1]
        elif elements[0] == "parent":
            parents = elements[1:]
        elif elements[0] == "author":
            author = elements[1]
        elif elements[0] == "committer":
            committer = elements[1]
        elif el != "":
            message = el
    return Commit(tree_hash, parents, author, committer, message)


def parse_tree(blobs: dict[str, Blob], tree_root: Blob, ignore_missing: bool = True) -> Tree:
    """
    Parse tree blob
    :param blobs: all read blobs (by traverse_objects)
    :param tree_root: tree blob to parse
    :param ignore_missing: ignore blobs which were not found in objects directory
    :return: tree contains children blobs (or only part of them found in objects directory)
    NB. Children blobs are not being parsed according to type.
        Also nested tree blobs are not being traversed.
    """
    children_mapping = {}
    content = tree_root.content.split(b' ', 1)[1].split(b' ')
    elements = [el.split(b'\x00', 1) for el in content]
    for i in range(len(elements)):
        elements[i][1] = elements[i][1][:20]
    for ssh in elements:
        if ssh[1].hex() in blobs.keys():
            children_mapping[ssh[0].decode()] = blobs[ssh[1].hex()]
    return Tree(children_mapping)


def find_initial_commit(blobs: dict[str, Blob]) -> Commit:
    """
    Iterate over blobs and find initial commit (without parents)
    :param blobs: blobs read from objects dir
    :return: initial commit
    """
    for blob in blobs.values():
        if blob.type_ == BlobType.COMMIT:
            if not [line for line in blob.content.decode().splitlines() if line.startswith('parent')]:
                return parse_commit(blob)
    assert False, 'Initial commit not found'


def search_file(blobs: dict[str, Blob], tree_root: Blob, filename: str) -> Blob:
    """
    Traverse tree blob (can have nested tree blobs) and find requested file,
    check if file was not found (assertion).
    :param blobs: blobs read from objects dir
    :param tree_root: root blob for traversal
    :param filename: requested file
    :return: requested file blob
    """
    content = tree_root.content.split(b' ', 1)[1].split(b' ')
    elements = [el.split(b'\x00', 1) for el in content]
    for i in range(len(elements)):
        elements[i][1] = elements[i][1][:20]

    for el in elements:
        sha1 = el[1].hex()
        if el[0].decode() == filename and sha1 in blobs:
            return blobs[sha1]
        if sha1 is not None and sha1 in blobs:
            if (blob := blobs[sha1]).type_ == BlobType.TREE:
                answer = search_file(blobs, blob, filename)
                if answer is not None:
                    return answer

    assert False, f'File {filename} not found in tree'
