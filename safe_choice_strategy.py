# safe_choice_strategy.py
from typing import List, Optional, Tuple
from Strategy import Strategy

Coord = Tuple[int, int]
Matrix = List[List[object]]  # numbers or '-' for used cells


class SafeChoiceStrategy(Strategy):
    """
    Strategy that scores each available cell (i, j) with a tuple:
        S[i,j] = (value, a(i,j), b(i,j))
    where
      a(i,j) = (-1)^( multiplicity of the row's max when excluding (i,j) ),
      b(i,j) = (-1)^( multiplicity of the column's max when excluding (i,j) ).

    Selection rule among valid moves:
      1) Maximize cell value.
      2) Among those with maximal value, prefer a=1 and b=1 (more 1's first).
      3) If still tied, prefer a=1 over -1, then b=1 over -1.
      4) Finally break ties deterministically by choosing the bottom-rightmost cell.

    Valid moves follow the game's rule:
      - If last_move is None: any non-'-' cell.
      - Else: any non-'-' cell in the same row or column as last_move.
    """

    # ---- public API ----
    def move(self, matrix: Matrix, last_move: Optional[Coord]) -> Optional[Coord]:
        n = len(matrix)
        if n == 0:
            return None

        # Build per-row and per-column top-2 summaries over available cells
        row_summ = [self._top2_summary_row(matrix, i) for i in range(n)]
        col_summ = [self._top2_summary_col(matrix, j) for j in range(n)]

        # Enumerate valid candidates
        candidates = self._valid_moves(matrix, last_move)
        if not candidates:
            return None

        # Primary: maximize value
        max_val = max(self._cell_value(matrix, i, j) for (i, j) in candidates)
        top_val_moves = [(i, j) for (i, j) in candidates if self._cell_value(matrix, i, j) == max_val]

        # Compute a(i,j), b(i,j) cheaply from summaries; then apply tie-breaks
        best = None
        best_key = None

        for (i, j) in top_val_moves:
            v = max_val
            a = self._parity_from_row_excluding(i, j, v, row_summ[i])
            b = self._parity_from_col_excluding(i, j, v, col_summ[j])

            # Prefer both = 1, then number of 1's, then a, then b, then position
            ones = (1 if a == 1 else 0) + (1 if b == 1 else 0)
            key = (ones, a, b, -i, -j)  # deterministic final tie-break

            if best_key is None or key > best_key:
                best_key = key
                best = (i, j)

        return best

    # ---- helpers: validity & value ----
    @staticmethod
    def _cell_value(matrix: Matrix, i: int, j: int) -> float:
        return matrix[i][j]  # assumed numeric when available

    @staticmethod
    def _is_free(val: object) -> bool:
        return val != '-'

    def _valid_moves(self, matrix: Matrix, last_move: Optional[Coord]) -> List[Coord]:
        n = len(matrix)
        if last_move is None:
            return [(i, j) for i in range(n) for j in range(n) if self._is_free(matrix[i][j])]
        r0, c0 = last_move
        out: List[Coord] = []
        # same row
        for j in range(n):
            if self._is_free(matrix[r0][j]):
                out.append((r0, j))
        # same column (avoid double-count if (r0,c0) still free)
        for i in range(n):
            if self._is_free(matrix[i][c0]) and (i, c0) not in out:
                out.append((i, c0))
        return out

    # ---- helpers: summaries and parity computation ----
    # Row/Col summary format: (top1_val, top1_cnt, top2_val, top2_cnt)
    # If top2 doesn't exist, store (None, 0) for it; if the line is empty, store (None, 0, None, 0)

    @staticmethod
    def _top2_summary_row(matrix: Matrix, i: int) -> Tuple[Optional[float], int, Optional[float], int]:
        vals = [matrix[i][j] for j in range(len(matrix)) if matrix[i][j] != '-']
        return SafeChoiceStrategy._top2_from_values(vals)

    @staticmethod
    def _top2_summary_col(matrix: Matrix, j: int) -> Tuple[Optional[float], int, Optional[float], int]:
        vals = [matrix[i][j] for i in range(len(matrix)) if matrix[i][j] != '-']
        return SafeChoiceStrategy._top2_from_values(vals)

    @staticmethod
    def _top2_from_values(vals: List[float]) -> Tuple[Optional[float], int, Optional[float], int]:
        if not vals:
            return (None, 0, None, 0)
        # Track counts
        counts = {}
        for x in vals:
            counts[x] = counts.get(x, 0) + 1
        # Sort distinct values descending
        distinct = sorted(counts.keys(), reverse=True)
        top1 = distinct[0]
        cnt1 = counts[top1]
        if len(distinct) >= 2:
            top2 = distinct[1]
            cnt2 = counts[top2]
        else:
            top2, cnt2 = None, 0
        return (top1, cnt1, top2, cnt2)

    @staticmethod
    def _parity_from_row_excluding(i: int, j: int, v_ij: float,
                                   row_summary: Tuple[Optional[float], int, Optional[float], int]) -> int:
        top1, cnt1, top2, cnt2 = row_summary
        if top1 is None:          # empty row ⇒ even multiplicity (0)
            return 1
        if v_ij == top1:
            if cnt1 > 1:
                m = cnt1 - 1          # still max, reduced multiplicity
            else:
                # removing the only top1 makes top2 the new max (may be None)
                m = cnt2
        else:
            # excluding (i,j) doesn't change row max nor its multiplicity
            m = cnt1
        return 1 if (m % 2 == 0) else -1

    @staticmethod
    def _parity_from_col_excluding(i: int, j: int, v_ij: float,
                                   col_summary: Tuple[Optional[float], int, Optional[float], int]) -> int:
        top1, cnt1, top2, cnt2 = col_summary
        if top1 is None:
            return 1
        if v_ij == top1:
            if cnt1 > 1:
                m = cnt1 - 1
            else:
                m = cnt2
        else:
            m = cnt1
        return 1 if (m % 2 == 0) else -1
