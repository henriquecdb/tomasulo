LATENCIAS = {
    'LDF': 2,
    'SDF': 2,
    'ADDF': 3,
    'SUBF': 3,
    'MULF': 5,
    'DIVF': 10
}


class ReservationStation:
    def __init__(self, name, op_type):
        self.name = name
        self.busy = False
        self.op = None
        self.vj = None
        self.vk = None
        self.qj = None
        self.qk = None
        self.a = None
        self.result = None
        self.cycles_left = 0
        self.op_type = op_type

    def clear(self):
        self.busy = False
        self.op = None
        self.vj = None
        self.vk = None
        self.qj = None
        self.qk = None
        self.a = None
        self.result = None
        self.cycles_left = 0


class Instruction:
    def __init__(self, line):
        parts = line.strip().replace(',', '').split()
        self.op = parts[0].upper()
        self.dest = parts[1]

        if self.op in ['LDF', 'SDF']:
            addr_str = parts[2].strip('[]')
            self.addr = int(addr_str)
            self.src1 = None
            self.src2 = None
        else:
            self.src1 = parts[2]
            self.src2 = parts[3]
            self.addr = None

        self.issue = None
        self.start_exec = None
        self.end_exec = None
        self.write_result = None
        self.rs = None


class TomasuloSimulator:
    def __init__(self):
        self.registers = {f'F{i}': 0.0 for i in range(8)}
        self.register_status = {f'F{i}': None for i in range(8)}
        self.memory = {}
        self.instructions = []
        self.pc = 0
        self.cycle = 0
        self.initial_memory = {}

        self.rs_add = [ReservationStation(
            f'Add{i + 1}', 'add') for i in range(3)]
        self.rs_mul = [ReservationStation(
            f'Mul{i + 1}', 'mul') for i in range(2)]
        self.rs_load = [ReservationStation(
            f'Load{i + 1}', 'load') for i in range(2)]

    def reset(self):
        self.registers = {f'F{i}': 0.0 for i in range(8)}
        self.register_status = {f'F{i}': None for i in range(8)}
        self.memory = dict(self.initial_memory)
        self.pc = 0
        self.cycle = 0

        for rs in self.rs_add + self.rs_mul + self.rs_load:
            rs.clear()

        for instr in self.instructions:
            instr.issue = None
            instr.start_exec = None
            instr.end_exec = None
            instr.write_result = None
            instr.rs = None

    def load_program(self, program_text, initial_memory=None):
        self.instructions = []
        for line in program_text.strip().split('\n'):
            line = line.split(';')[0].strip()
            if line:
                self.instructions.append(Instruction(line))

        if initial_memory:
            self.initial_memory = dict(initial_memory)
            self.memory = dict(initial_memory)
        else:
            self.initial_memory = {}
            self.memory = {}

    def get_rs_for_op(self, op):
        if op in ['ADDF', 'SUBF']:
            return self.rs_add
        if op in ['MULF', 'DIVF']:
            return self.rs_mul
        if op in ['LDF', 'SDF']:
            return self.rs_load
        return []

    def issue(self):
        if self.pc >= len(self.instructions):
            return False

        instr = self.instructions[self.pc]
        if instr.issue is not None:
            return False

        rs_list = self.get_rs_for_op(instr.op)
        free_rs = None
        for rs in rs_list:
            if not rs.busy:
                free_rs = rs
                break

        if free_rs is None:
            return False

        free_rs.busy = True
        free_rs.op = instr.op
        instr.issue = self.cycle
        instr.rs = free_rs.name

        if instr.op in ['LDF', 'SDF']:
            free_rs.a = instr.addr
            if instr.op == 'SDF':
                if self.register_status[instr.dest] is None:
                    free_rs.vj = self.registers[instr.dest]
                    free_rs.qj = None
                else:
                    free_rs.qj = self.register_status[instr.dest]
                    free_rs.vj = None
            else:
                self.register_status[instr.dest] = free_rs.name
        else:
            if self.register_status[instr.src1] is None:
                free_rs.vj = self.registers[instr.src1]
                free_rs.qj = None
            else:
                free_rs.qj = self.register_status[instr.src1]
                free_rs.vj = None

            if self.register_status[instr.src2] is None:
                free_rs.vk = self.registers[instr.src2]
                free_rs.qk = None
            else:
                free_rs.qk = self.register_status[instr.src2]
                free_rs.vk = None

            self.register_status[instr.dest] = free_rs.name

        self.pc += 1
        return True

    def execute(self):
        all_rs = self.rs_add + self.rs_mul + self.rs_load

        for rs in all_rs:
            if not rs.busy:
                continue

            if rs.cycles_left == 0:
                if rs.op in ['LDF', 'SDF']:
                    if rs.op == 'SDF' and rs.qj is not None:
                        continue
                    rs.cycles_left = LATENCIAS[rs.op]
                    for instr in self.instructions:
                        if instr.rs == rs.name and instr.start_exec is None:
                            instr.start_exec = self.cycle
                else:
                    if rs.qj is not None or rs.qk is not None:
                        continue
                    rs.cycles_left = LATENCIAS[rs.op]
                    for instr in self.instructions:
                        if instr.rs == rs.name and instr.start_exec is None:
                            instr.start_exec = self.cycle

            if rs.cycles_left > 0:
                rs.cycles_left -= 1

                if rs.cycles_left == 0:
                    if rs.op == 'LDF':
                        rs.result = self.memory.get(rs.a, 0.0)
                    elif rs.op == 'SDF':
                        pass
                    elif rs.op == 'ADDF':
                        rs.result = rs.vj + rs.vk
                    elif rs.op == 'SUBF':
                        rs.result = rs.vj - rs.vk
                    elif rs.op == 'MULF':
                        rs.result = rs.vj * rs.vk
                    elif rs.op == 'DIVF':
                        rs.result = rs.vj / rs.vk if rs.vk != 0 else 0.0

                    for instr in self.instructions:
                        if instr.rs == rs.name and instr.end_exec is None:
                            instr.end_exec = self.cycle

    def write_result(self):
        all_rs = self.rs_add + self.rs_mul + self.rs_load

        for rs in all_rs:
            if not rs.busy:
                continue

            found_instr = None
            for instr in self.instructions:
                if instr.rs == rs.name and instr.end_exec is not None and instr.write_result is None:
                    found_instr = instr
                    break

            if found_instr is None:
                continue

            if rs.op == 'SDF':
                self.memory[rs.a] = rs.vj
            else:
                dest_reg = found_instr.dest
                self.registers[dest_reg] = rs.result
                if self.register_status[dest_reg] == rs.name:
                    self.register_status[dest_reg] = None

            for other_rs in all_rs:
                if other_rs.qj == rs.name:
                    other_rs.vj = rs.result
                    other_rs.qj = None
                if other_rs.qk == rs.name:
                    other_rs.vk = rs.result
                    other_rs.qk = None

            found_instr.write_result = self.cycle
            rs.clear()

    def step(self):
        self.cycle += 1
        self.write_result()
        self.execute()
        self.issue()

    def is_finished(self):
        if self.pc < len(self.instructions):
            return False
        for rs in self.rs_add + self.rs_mul + self.rs_load:
            if rs.busy:
                return False
        return True
