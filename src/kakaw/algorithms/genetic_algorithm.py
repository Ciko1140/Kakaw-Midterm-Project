from random import Random

from kakaw.algorithms.base import LocalSearch
from kakaw.problems import Problem, State


class GeneticAlgorithm(LocalSearch):
    """
    Deskripsi:
      Kelas utama untuk Genetic Algorithm
    """

    def __init__(
        self, problem: Problem, N: int = 50, G: int = 200,
        p_c: float = 0.8, p_m: float = 0.1, elit: int = 2, seed: int = 42,
    ) -> None:
        super().__init__(problem)
        if type(N) is not int or N < 3:
            raise ValueError("N harus integer >= 3 untuk tournament")
        if type(G) is not int or G < 0:
            raise ValueError("G harus integer >= 0")
        if type(elit) is not int or not 0 <= elit <= N:
            raise ValueError("elit harus integer antara 0 dan N")
        if not 0 <= p_c <= 1 or not 0 <= p_m <= 1:
            raise ValueError("p_c dan p_m harus berada pada [0, 1]")
        self.N = N
        self.G = G
        self.p_c = p_c
        self.p_m = p_m
        self.elit = elit
        self.seed = seed

    def search(self) -> State:
        objective = self.problem.objective
        objective.evaluations = 0
        rng = Random(self.seed)
        initial = self.initial_state.copy()
        initial_score = objective.evaluate(initial)
        population = [(initial_score, initial)]
        self.iteration = 0
        self.history = []

        while len(population) < self.N:
            candidate = initial.copy()
            for class_id in candidate.assignments:
                candidate = self.problem.random_relocate(candidate, class_id, rng)
            score = objective.evaluate(candidate)
            population.append((score, candidate))

        for _ in range(self.G):
            population.sort(key=self._score)
            new_population = population[:self.elit]
            while len(new_population) < self.N:
                first = self._tournament(population, rng)
                second = self._tournament(population, rng)
                child = first.copy()
                if rng.random() < self.p_c:
                    child = self._crossover(first, second, rng)
                child = self._mutate(child, rng)
                score = objective.evaluate(child)
                new_population.append((score, child))

            population = new_population
            self.iteration += 1
            best = min(population, key=self._score)
            self.history.append(best[0])

        best = min(population, key=self._score)
        self.goal_state = best[1]
        return self.goal_state

    def _score(self, individual):
        return individual[0]

    def _tournament(self, population: list[tuple[float, State]], rng: Random) -> State:
        participants = rng.sample(population, 3)
        winner = participants[0]
        for individual in participants[1:]:
            if individual[0] < winner[0]:
                winner = individual
        return winner[1]

    def _crossover(self, first: State, second: State, rng: Random) -> State:
        assignments = {}
        for class_id in first.assignments:
            if rng.random() < 0.5:
                assignments[class_id] = first.assignments[class_id]
            else:
                assignments[class_id] = second.assignments[class_id]
        return State(assignments)

    def _mutate(self, state: State, rng: Random) -> State:
        for class_id in state.assignments:
            if rng.random() < self.p_m:
                state = self.problem.random_relocate(state, class_id, rng)
        return state
