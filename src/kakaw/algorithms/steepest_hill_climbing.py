from kakaw.algorithms.base import LocalSearch
from kakaw.problems import Problem, State

class SteepestHillClimbing(LocalSearch):
    """
    Deskripsi:
      Kelas utama untuk algoritma Steepest Ascent Hill Climbing
    """

    def __init__(self, initial_state) -> None:
        super().__init__(initial_state)

    def search(self) -> State:
        pass
