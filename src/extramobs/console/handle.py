import sys
from enum import IntEnum

from colorama import just_fix_windows_console


class ETerminalClearMode(IntEnum):
    All = 2
    AllSpecial = 3
    FromCursorToEnd = 0
    FromCursorToBeginning = 1


class StaticConsoleHandle:
    default_width = 50

    @staticmethod
    def init():
        just_fix_windows_console()

    @staticmethod
    def move_cursor(x: int = None, y: int = None):
        if x is None:
            x = ""
        if y is None:
            y = ""

        sys.stdout.write(f"\033[{y};{x}H")

    @staticmethod
    def move_cursor_x(x: int = None):
        if x is None:
            x = ""

        sys.stdout.write(f"\033[{x}G")

    @classmethod
    def move_cursor_y(cls, y: int = None):
        if y is None:
            y = ""

        cls.move_cursor(None, y)

    @classmethod
    def clear_terminal(
        cls,
        cursor_position: tuple = None,
        mode: ETerminalClearMode = ETerminalClearMode.FromCursorToBeginning,
    ):
        if cursor_position is None:
            cursor_position = (None, None)

        sys.stdout.write(f"\033[{mode.value}J")
        cls.move_cursor(cursor_position[0], cursor_position[1])

    @staticmethod
    def move_cursor_up(quantity: int = 1):
        sys.stdout.write(f"\033[{quantity}A")

    @classmethod
    def draw_horizontal(cls, seq: str, width: int = None, end_line: str = "\n"):
        if width is None:
            width = cls.default_width

        output = []
        for i in range(width):
            if i * len(seq) >= width:
                output[-1][: width % len(seq)]
                break
            output.append(seq)

        sys.stdout.write(f"{''.join(output)}{end_line}")

    @classmethod
    def draw_text(
        cls, text: str, width: int = None, end_line: str = "\n", centered: bool = False
    ):
        if width is None:
            width = cls.default_width

        if centered:
            text = text.center(width)

        sys.stdout.write(f"{text}{end_line}")

    @classmethod
    def draw_new_line(cls, quantity_lines: int = 1):
        sys.stdout.write(f"\n" * quantity_lines)

    @classmethod
    def draw_progress_bar(
        cls, current_value: int, target_value: int, bar_scale: int = 3
    ):
        percent_progress = current_value / target_value * 100
        cls.draw_text(
            f"\t{(int(percent_progress/bar_scale)*'█') + (int(100/bar_scale) - int(percent_progress/bar_scale)) * '░'}  {percent_progress:.2f} %",
            end_line="",
        )
        cls.move_cursor_x()
