from kakaw.algorithms.base import LocalSearch
from kakaw.problems import Problem, State


class GeneticAlgorithm(LocalSearch):
    """
    Deskripsi:
      Kelas utama untuk Genetic Algorithm
    """

    def __init__(self, problem: Problem) -> None:
        super().__init__(problem)

    def search(self) -> State:
        pass
