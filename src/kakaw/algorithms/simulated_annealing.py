from kakaw.algorithms.base import LocalSearch
from kakaw.problems import Problem, State

class SimulatedAnnealing(LocalSearch):
    """
    Deskripsi:
      Kelas utama untuk algoritma Simulated Annealing
    """

    def __init__(self, initial_state) -> None:
        super().__init__(initial_state)

    def search(self) -> State:
        pass
