import os
import numpy as np

def load_board_until_ok():
    """
    Keep asking for a filename until we can read a valid square integer matrix.
    Uses 'with open(input_file_name, "rt") as input_file:' as required.
    """
    while True:
        name = input("Enter board filename (.txt optional): ").strip()
        if not name:
            print("Please enter a filename.\n")
            continue

        # Add .txt if missing
        root, ext = os.path.splitext(name)
        if ext == "":
            name = name + ".txt"

        # Build path (accept absolute or relative)
        input_file_name = name if os.path.isabs(name) else os.path.join(os.getcwd(), name)

        try:
            matrix_values = []

            # Required notation from your class:
            with open(input_file_name, 'rt') as input_file:  # rt means read only text
                for line_number, lines in enumerate(input_file, start=1):
                    parts = lines.strip().split(',')
                    row = []
                    for value in parts:
                        value = value.strip()
                        try:
                            row.append(int(value))
                        except ValueError:
                            raise ValueError(
                                f"Non-numeric value '{value}' on line {line_number}."
                            )
                    if row:  # skip empty lines
                        matrix_values.append(row)

            if not matrix_values:
                raise ValueError("The file is empty.")

            row_length = len(matrix_values[0])
            # Check consistent row sizes
            if any(len(row) != row_length for row in matrix_values):
                raise ValueError("Rows have inconsistent lengths.")
            # Check for square matrix
            if len(matrix_values) != row_length:
                raise ValueError("Matrix is not square (requires N×N).")

            matrix = np.array(matrix_values, dtype=object)
            return matrix

        except FileNotFoundError:
            print(f"File not found: {input_file_name}")
        except ValueError as e:
            print(f"Problem with file contents: {e}")
        except OSError as e:
            print(f"Could not read the file: {e}")

        print("Let's try again.\n")