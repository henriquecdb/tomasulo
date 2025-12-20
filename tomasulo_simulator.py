import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from tomasulo_core import TomasuloSimulator


class TomasuloGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Tomasulo")
        self.simulator = TomasuloSimulator()

        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(main_frame, text="Programa:").grid(row=0, column=0, sticky=tk.W)
        self.program_text = scrolledtext.ScrolledText(main_frame, width=50, height=8)
        self.program_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        ttk.Label(main_frame, text="Memória Inicial (ex: 50=1.5, 51=2.0):").grid(
            row=2, column=0, sticky=tk.W)
        self.memory_config = ttk.Entry(main_frame, width=50)
        self.memory_config.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        self.memory_config.insert(0, "50=1.5, 51=2.0, 52=4.0")

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=5)

        ttk.Button(btn_frame, text="Carregar Programa", command=self.load_program).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Carregar Arquivo", command=self.load_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Próximo Ciclo", command=self.next_cycle).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Executar Tudo", command=self.run_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Reset", command=self.reset).pack(side=tk.LEFT, padx=2)

        self.cycle_label = ttk.Label(main_frame, text="Ciclo: 0")
        self.cycle_label.grid(row=5, column=0, columnspan=2, pady=5)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        instr_frame = ttk.Frame(self.notebook)
        self.notebook.add(instr_frame, text="Instruções")

        self.instr_tree = ttk.Treeview(
            instr_frame,
            columns=('Instrução', 'Issue', 'Start', 'End', 'Write', 'RS'),
            show='headings',
            height=10,
        )
        for col, w in zip(
            ['Instrução', 'Issue', 'Start', 'End', 'Write', 'RS'],
            [200, 60, 80, 80, 100, 80]
        ):
            self.instr_tree.heading(col, text=col)
            self.instr_tree.column(col, width=w)

        self.instr_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        rs_frame = ttk.Frame(self.notebook)
        self.notebook.add(rs_frame, text="Reservation Stations")

        self.rs_text = scrolledtext.ScrolledText(rs_frame, width=80, height=15, font=('Courier', 10))
        self.rs_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        reg_frame = ttk.Frame(self.notebook)
        self.notebook.add(reg_frame, text="Registradores")

        self.reg_text = scrolledtext.ScrolledText(reg_frame, width=80, height=15, font=('Courier', 10))
        self.reg_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        mem_frame = ttk.Frame(self.notebook)
        self.notebook.add(mem_frame, text="Memória")

        self.mem_text = scrolledtext.ScrolledText(mem_frame, width=80, height=15, font=('Courier', 10))
        self.mem_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        example_program = """LDF F1, [50]
LDF F2, [51]
LDF F3, [52]
ADDF F4, F1, F2
MULF F5, F4, F3
SDF F5, [53]"""
        self.program_text.insert('1.0', example_program)

    def load_program(self):
        program = self.program_text.get('1.0', tk.END)
        mem_config_str = self.memory_config.get().strip()

        initial_memory = {}
        if mem_config_str:
            for item in mem_config_str.split(','):
                addr, val = item.split('=')
                initial_memory[int(addr.strip())] = float(val.strip())

        self.simulator.reset()
        self.simulator.load_program(program, initial_memory)
        self.update_display()

    def load_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename) as f:
                self.program_text.delete('1.0', tk.END)
                self.program_text.insert('1.0', f.read())
            self.load_program()

    def next_cycle(self):
        if not self.simulator.instructions or self.simulator.is_finished():
            return
        self.simulator.step()
        self.update_display()

    def run_all(self):
        while not self.simulator.is_finished():
            self.simulator.step()
        self.update_display()

    def reset(self):
        self.simulator.reset()
        self.update_display()

    def update_display(self):
        self.cycle_label.config(text=f"Ciclo: {self.simulator.cycle}")

        for item in self.instr_tree.get_children():
            self.instr_tree.delete(item)

        for instr in self.simulator.instructions:
            instr_str = f"{instr.op} {instr.dest}"
            instr_str += f", [{instr.addr}]" if instr.op in ['LDF', 'SDF'] else f", {instr.src1}, {instr.src2}"

            self.instr_tree.insert(
                '', tk.END,
                values=(
                    instr_str,
                    instr.issue or '-',
                    instr.start_exec or '-',
                    instr.end_exec or '-',
                    instr.write_result or '-',
                    instr.rs or '-',
                ),
            )

        self.rs_text.delete('1.0', tk.END)

        self.rs_text.insert(tk.END, "=== ADD/SUB Reservation Stations ===\n")
        self.rs_text.insert(tk.END, f"{'Nome':<8}{'Busy':<6}{'Op':<6}{'Vj':<10}{'Vk':<10}{'Qj':<8}{'Qk':<8}{'Ciclos':<8}\n")
        self.rs_text.insert(tk.END, "-" * 80 + "\n")
        for rs in self.simulator.rs_add:
            self.rs_text.insert(
                tk.END,
                f"{rs.name:<8}{str(rs.busy):<6}{rs.op or '-':<6}"
                f"{str(rs.vj) if rs.vj is not None else '-':<10}"
                f"{str(rs.vk) if rs.vk is not None else '-':<10}"
                f"{(rs.qj.name if rs.qj else '-'): <8}"
                f"{(rs.qk.name if rs.qk else '-'): <8}"
                f"{rs.cycles_left:<8}\n"
            )

        self.rs_text.insert(tk.END, "\n=== MUL/DIV Reservation Stations ===\n")
        self.rs_text.insert(tk.END, f"{'Nome':<8}{'Busy':<6}{'Op':<6}{'Vj':<10}{'Vk':<10}{'Qj':<8}{'Qk':<8}{'Ciclos':<8}\n")
        self.rs_text.insert(tk.END, "-" * 80 + "\n")
        for rs in self.simulator.rs_mul:
            self.rs_text.insert(
                tk.END,
                f"{rs.name:<8}{str(rs.busy):<6}{rs.op or '-':<6}"
                f"{str(rs.vj) if rs.vj is not None else '-':<10}"
                f"{str(rs.vk) if rs.vk is not None else '-':<10}"
                f"{(rs.qj.name if rs.qj else '-'): <8}"
                f"{(rs.qk.name if rs.qk else '-'): <8}"
                f"{rs.cycles_left:<8}\n"
            )

        self.rs_text.insert(tk.END, "\n=== LOAD/STORE Reservation Stations ===\n")
        self.rs_text.insert(tk.END, f"{'Nome':<8}{'Busy':<6}{'Op':<6}{'Addr':<10}{'Vj':<10}{'Qj':<8}{'Ciclos':<8}\n")
        self.rs_text.insert(tk.END, "-" * 80 + "\n")
        for rs in self.simulator.rs_load:
            self.rs_text.insert(
                tk.END,
                f"{rs.name:<8}{str(rs.busy):<6}{rs.op or '-':<6}"
                f"{str(rs.a) if rs.a is not None else '-':<10}"
                f"{str(rs.vj) if rs.vj is not None else '-':<10}"
                f"{(rs.qj.name if rs.qj else '-'): <8}"
                f"{rs.cycles_left:<8}\n"
            )

        self.reg_text.delete('1.0', tk.END)
        self.reg_text.insert(tk.END, f"{'Reg':<6}{'Valor':<15}{'Status (Qi)':<15}\n")
        self.reg_text.insert(tk.END, "-" * 40 + "\n")
        for reg in sorted(self.simulator.registers):
            self.reg_text.insert(
                tk.END,
                f"{reg:<6}{self.simulator.registers[reg]:<15.2f}{self.simulator.register_status[reg] or '-':<15}\n"
            )

        self.mem_text.delete('1.0', tk.END)
        self.mem_text.insert(tk.END, f"{'Endereço':<15}{'Valor':<15}\n")
        self.mem_text.insert(tk.END, "-" * 30 + "\n")
        for addr in sorted(self.simulator.memory):
            self.mem_text.insert(
                tk.END, f"{addr:<15}{self.simulator.memory[addr]:<15.2f}\n"
            )
