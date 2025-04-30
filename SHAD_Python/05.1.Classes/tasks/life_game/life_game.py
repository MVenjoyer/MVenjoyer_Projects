class LifeGame(object):
    """
    Class for Game life
    """

    def __init__(self, ocean: list[list[int]]) -> None:
        self.ocean = ocean
        self.width = len(ocean)
        self.height = len(ocean[0])

    def get_next_generation(self) -> list[list[int]]:
        new_ocean = [[0 for _ in range(self.height)] for _ in range(self.width)]
        for i in range(self.width):
            for j in range(self.height):
                neighbours = self._gen_neighbour(i, j)
                if self.ocean[i][j] == 0:
                    if neighbours['fi'] == 3:
                        new_ocean[i][j] = 2
                    elif neighbours['sh'] == 3:
                        new_ocean[i][j] = 3
                    else:
                        new_ocean[i][j] = 0
                elif self.ocean[i][j] == 1:
                    new_ocean[i][j] = 1
                elif self.ocean[i][j] == 2:
                    if neighbours['fi'] < 2 or neighbours['fi'] > 3:
                        new_ocean[i][j] = 0
                    else:
                        new_ocean[i][j] = 2
                elif self.ocean[i][j] == 3:
                    if neighbours['sh'] < 2 or neighbours['sh'] > 3:
                        new_ocean[i][j] = 0
                    else:
                        new_ocean[i][j] = 3
        self.ocean = new_ocean
        return new_ocean

    def _get_marker(self, x: int, y: int) -> str:
        if not self._check_border(x, y):
            return 'em'
        match self.ocean[x][y]:
            case 0:
                return 'em'
            case 1:
                return 'mo'
            case 2:
                return 'fi'
            case 3:
                return 'sh'
        return 'em'

    def _check_border(self, x: int, y: int) -> bool:
        return 0 <= x < len(self.ocean) and 0 <= y < len(self.ocean[0])

    def _gen_neighbour(self, x: int, y: int) -> dict[str, int]:
        answer: dict[str, int] = {'em': 0, 'mo': 0, 'fi': 0, 'sh': 0}
        if self._check_border(x - 1, y - 1):
            answer[self._get_marker(x - 1, y - 1)] += 1
        if self._check_border(x - 1, y):
            answer[self._get_marker(x - 1, y)] += 1
        if self._check_border(x + 1, y):
            answer[self._get_marker(x + 1, y)] += 1
        if self._check_border(x, y - 1):
            answer[self._get_marker(x, y - 1)] += 1
        if self._check_border(x + 1, y + 1):
            answer[self._get_marker(x + 1, y + 1)] += 1
        if self._check_border(x, y + 1):
            answer[self._get_marker(x, y + 1)] += 1
        if self._check_border(x + 1, y - 1):
            answer[self._get_marker(x + 1, y - 1)] += 1
        if self._check_border(x - 1, y + 1):
            answer[self._get_marker(x - 1, y + 1)] += 1
        return answer
