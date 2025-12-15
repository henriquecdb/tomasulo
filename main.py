import tkinter as tk
from tomasulo_simulator import TomasuloGUI


def main():
    root = tk.Tk()
    TomasuloGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
