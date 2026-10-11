from abc import ABC, abstractmethod

import matplotlib.pyplot as plt

from kakaw.problems import Problem, State


class LocalSearch(ABC):
    """
    Deskripsi:
      Abstract class untuk algoritma local search.
    """

    def __init__(self, problem: Problem) -> None:
        self.problem: Problem = problem
        self.initial_state: State = problem.initial_state()
        self.goal_state: State | None = None
        self.iteration: int = 0
        self.history: list[float] = []

    @abstractmethod
    def search(self) -> State:
        """Method wajib untuk menjalankan algoritma."""

    def plot(self, path: str | None = None) -> None:
        """Plot objective per move diterima; simpan ke `path` bila diberi."""
        if not self.history:
            print("No data to plot")
            return
        plt.plot(range(len(self.history)), self.history, marker="o")
        plt.xlabel("iterasi")
        plt.ylabel("F")
        plt.title(type(self).__name__)
        if path is None:
            plt.show()
        else:
            plt.savefig(path)
        plt.close()
