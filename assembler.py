"""
Hack assembler: .asm -> .hack
Usage: python assembler.py Prog.asm

K = 01
Extra feature: Save labels and variables with their addresses in symbols.txt.
"""

import sys

# Binary codes for Hack Assembly computations
COMP = {
    '0': '0101010', '1': '0111111', '-1': '0111010',
    'D': '0001100', 'A': '0110000', '!D': '0001101', '!A': '0110001',
    '-D': '0001111', '-A': '0110011', 'D+1': '0011111', 'A+1': '0110111',
    'D-1': '0001110', 'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011',
    'A-D': '0000111', 'D&A': '0000000', 'D|A': '0010101',
}

# Generate M-based computation codes from A-based codes
for k, v in list(COMP.items()):
    if 'A' in k:
        COMP[k.replace('A', 'M')] = '1' + v[1:]

# Add alternative computation expressions
for a, b in [('A+D', 'D+A'), ('M+D', 'D+M'), ('A&D', 'D&A'),
             ('M&D', 'D&M'), ('A|D', 'D|A'), ('M|D', 'D|M')]:
    COMP[a] = COMP[b]

# Binary codes for jump instructions
JUMP = {
    '': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011',
    'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'
}

# Predefined Hack computer symbols and memory addresses
SYMBOLS = {
    'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
    'SCREEN': 16384, 'KBD': 24576
}

# Define R0 to R15 register symbols
for i in range(16):
    SYMBOLS['R' + str(i)] = i


def dest_bits(d):
    """Convert destination into A, D, M binary bits."""
    return ('1' if 'A' in d else '0') + \
           ('1' if 'D' in d else '0') + \
           ('1' if 'M' in d else '0')


def clean(line):
    """Remove comments and all whitespace from a line."""
    line = line.split('//')[0]
    return ''.join(line.split())


def assemble(lines):
    """Convert Hack Assembly instructions into binary machine code."""

    symbols = dict(SYMBOLS)
    program = []
    saved_symbols = {}

    # First pass: Identify labels and store their ROM addresses
    for raw in lines:
        line = clean(raw)

        if not line:
            continue

        if line.startswith('(') and line.endswith(')'):
            name = line[1:-1]

            # Save label and its ROM address
            symbols[name] = len(program)
            saved_symbols[name] = len(program)

        else:
            program.append(line)

    # Second pass: Convert instructions into 16-bit binary
    output = []
    next_var = 16

    for line in program:
        # A-instruction: Starts with @
        if line.startswith('@'):
            value = line[1:]

            if value.isdigit():
                n = int(value)
            else:
                # Assign RAM addresses to new variables
                if value not in symbols:
                    symbols[value] = next_var
                    saved_symbols[value] = next_var
                    next_var += 1

                n = symbols[value]

            output.append(format(n, '016b'))

        else:
            # C-instruction: Separate dest, comp and jump
            dest, jump = '', ''
            comp = line

            if '=' in comp:
                dest, comp = comp.split('=', 1)

            if ';' in comp:
                comp, jump = comp.split(';', 1)

            # Generate final 16-bit C-instruction
            output.append(
                '111' + COMP[comp] + dest_bits(dest) + JUMP[jump]
            )

    return output, saved_symbols


def main():
    # Check command-line arguments
    if len(sys.argv) != 2 or not sys.argv[1].endswith('.asm'):
        print("Usage: python assembler.py Prog.asm")
        sys.exit(1)

    path = sys.argv[1]

    # Read the assembly file
    with open(path) as f:
        lines = f.read().splitlines()

    # Assemble the program
    result, saved_symbols = assemble(lines)

    # Generate output .hack filename
    out_path = path[:-4] + '.hack'

    # Write binary instructions into the .hack file
    with open(out_path, 'w') as f:
        f.write('\n'.join(result) + '\n')

    # Save labels and variables in symbols.txt
    with open('symbols.txt', 'w') as f:
        f.write("Symbol\tAddress\n")
        f.write("----------------\n")

        for name, address in saved_symbols.items():
            f.write(f"{name}\t{address}\n")

    print(f"Wrote {len(result)} instructions to {out_path}")
    print("Symbol addresses saved in symbols.txt")


# Execute main function when this file runs directly
if __name__ == '__main__':
    main()