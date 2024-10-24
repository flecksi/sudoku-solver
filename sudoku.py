from ortools.sat.python import cp_model
from pydantic import BaseModel, field_validator, ValidationError
import numpy as np
import pandas as pd
import random


class SudokuBoard(BaseModel):
    cells: list[list[int]]

    def as_dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame(
            self.cells, columns=("A", "B", "C", "D", "E", "F", "G", "H", "I")
        )
        # df.columns.rename(, inplace=True)
        return df

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> "SudokuBoard":
        return cls(
            cells=[
                [
                    (
                        df.loc[r, df.columns[c]]
                        if not pd.isna(
                            df.loc[r, df.columns[c]]
                        )  # isinstance(df.loc[r, df.columns[c]], float)
                        else 0
                    )
                    for c in range(9)
                ]
                for r in range(9)
            ]
        )

    @classmethod
    def empty(cls) -> "SudokuBoard":
        return cls(cells=[[0 for c in range(9)] for r in range(9)])

    @classmethod
    def from_cell_dict(cls, cell_dict: dict[tuple[int, int], int]):
        return cls(
            cells=[
                [cell_dict[r, c] if (r, c) in cell_dict else 0 for c in range(9)]
                for r in range(9)
            ]
        )

    @classmethod
    def random_slow(cls, n_places_to_fill: int) -> "SudokuBoard":
        cells = [[0 for c in range(9)] for r in range(9)]
        n = 0
        n_tries = 0

        while n < n_places_to_fill:
            n_tries += 1
            if n_tries > 1_000:
                break

            r_pick = np.random.randint(0, 9)
            c_pick = np.random.randint(0, 9)
            if cells[r_pick][c_pick] != 0:
                continue

            cells[r_pick][c_pick] = np.random.randint(1, 10)
            if not SudokuBoard(cells=cells).is_valid():
                cells[r_pick][c_pick] = 0
            else:
                n += 1

        return cls(cells=cells)

    @classmethod
    def random(cls, n_places_to_fill: int) -> "SudokuBoard":
        cells = [[0 for c in range(9)] for r in range(9)]
        cells[0] = random.sample(range(1, 10), 9)
        cells_solved = SudokuBoard(cells=cells).solve()[0].cells

        n = 0
        n_tries = 0

        while n < (81 - n_places_to_fill):
            n_tries += 1
            if n_tries > 1_000:
                break

            r_pick = np.random.randint(0, 9)
            c_pick = np.random.randint(0, 9)
            if cells_solved[r_pick][c_pick] == 0:
                continue

            cells_solved[r_pick][c_pick] = 0
            n += 1

        return SudokuBoard(cells=cells_solved)

    def solve(self, n_max_solutions: int = 1) -> list["SudokuBoard"]:

        class SolutionPrinter(cp_model.CpSolverSolutionCallback):
            """Print intermediate solutions."""

            def __init__(
                self,
                x: dict[tuple[int, int], cp_model.IntVar],
                stop_after_n_solutions: int,
            ):
                cp_model.CpSolverSolutionCallback.__init__(self)
                self.__x = x
                self.__solution_count = 0
                self.__stop_after_n_solutions = stop_after_n_solutions
                self.__solution_cells = []

            def on_solution_callback(self) -> None:
                self.__solution_count += 1
                self.__solution_cells.append(
                    [
                        [self.value(self.__x[row, col]) for col in range(9)]
                        for row in range(9)
                    ]
                )

                if self.__solution_count >= self.__stop_after_n_solutions:
                    self.StopSearch()

            @property
            def solution_count(self) -> int:
                return self.__solution_count

            @property
            def solutions(self) -> list[list[list[int]]]:
                return self.__solution_cells

        model = cp_model.CpModel()

        x = {}

        for row in range(9):
            for col in range(9):
                x[row, col] = model.new_int_var(1, 9, f"row{row}_col{col}")
                if self.cells[row][col] != 0:
                    model.add(x[row, col] == self.cells[row][col])

        # all values in a row must be different
        for row in range(9):
            model.add_all_different([x[row, col] for col in range(9)])

        # all values in a column must be different
        for col in range(9):
            model.add_all_different([x[row, col] for row in range(9)])

        # all values in 3x3 blocks must be different
        for i in range(3):
            row_range = range(i * 3, i * 3 + 3)
            for j in range(3):
                col_range = range(j * 3, j * 3 + 3)
                model.add_all_different(
                    [x[row, col] for row in row_range for col in col_range]
                )

        solver = cp_model.CpSolver()
        solution_printer = SolutionPrinter(x=x, stop_after_n_solutions=n_max_solutions)
        solver.parameters.enumerate_all_solutions = True
        # solver.parameters.random_seed = 987871
        status = solver.solve(model, solution_printer)

        return [
            SudokuBoard(cells=solution_cells)
            for solution_cells in solution_printer.solutions
        ]

    def draw(self, indent: int = 0, zero_char: str = " ", hfill: int = 1) -> str:
        rv_string = ""
        for row in range(9):
            if (row > 0) and (row % 3 == 0):
                rv_string += (
                    " " * indent
                    + "-" * (3 + 6 * hfill)
                    + "+"
                    + "-" * (3 + 6 * hfill)
                    + "+"
                    + "-" * (3 + 6 * hfill)
                    + "\n"
                )
            rv_string += " " * indent
            for col in range(9):
                if (col > 0) and (col % 3 == 0):
                    rv_string += "|"
                v = str(self.cells[row][col]) if self.cells[row][col] > 0 else zero_char
                rv_string += " " * hfill + v + " " * hfill
            rv_string += "\n" if row < 8 else ""

        return rv_string

    def is_valid(self) -> bool:
        if len(self.solve()) > 0:
            return True
        else:
            return False

    @property
    def n_filled(self) -> int:
        n = 0
        for r in range(9):
            for c in range(9):
                if self.cells[r][c] > 0:
                    n += 1
        return n

    @field_validator("cells")
    @classmethod
    def check_board(cls, cells: list[list[int]]):
        if len(cells) != 9:
            raise ValueError("board must have 9 rows")
        for r in range(9):
            if len(cells[r]) != 9:
                raise ValueError("board must have 9 columns")
            if any([v not in range(0, 10) for v in cells[r]]):
                raise ValueError("Values must be between 0 and 9")

        return cells

    class Config:
        frozen = True


if __name__ == "__main__":
    print("Empty Board:")
    b_empty = SudokuBoard.empty()
    print(b_empty.draw(indent=3))

    b_solved = b_empty.solve()

    print("\nSolution:")
    print(b_solved[0].draw(indent=3))

    print("\nFilled Board:")
    b_with_numbers = SudokuBoard.from_cell_dict(
        {
            (0, 0): 1,
            (0, 1): 2,
            (0, 2): 3,
            (3, 3): 1,
            (3, 4): 2,
            (3, 5): 3,
            (6, 6): 1,
            (6, 7): 2,
            (6, 8): 3,
        }
    )
    print(b_with_numbers.draw(indent=3))
    b_solved = b_with_numbers.solve(n_max_solutions=1)

    for i_s, s in enumerate(b_solved):
        print(f"\nSolution {i_s+1}:")
        print(s.draw(indent=3))

    print(f"{b_with_numbers.is_valid()=}")

    b_random = SudokuBoard.random(n_places_to_fill=28)
    print(f"\nRandom Board ({b_random.n_filled} cells filled)")
    print(b_random.draw(indent=3))
    b_random_solved = b_random.solve(n_max_solutions=100)
    print(f"Has {len(b_random_solved)} solutions")
    df = b_random_solved[0].as_dataframe()
    b_from_df = SudokuBoard.from_dataframe(df)
    print(b_from_df.draw(indent=3))

    for i in range(20):
        rand_seq = random.sample(range(1, 10), 9)
        print(f"{rand_seq}, {len(rand_seq)=}", end="")
        for n in range(1, 10):
            print(f"{n}:{sum([i==n for i in rand_seq])}, ", end="")
        print("")
