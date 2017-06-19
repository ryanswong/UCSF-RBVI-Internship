# vim: set expandtab shiftwidth=4 softtabstop=4:

import sys
print(sys.version + "\n" + sys.executable)
print("-"*50 + "\n")

# def open_mol2(session, stream, name):
#     structures = []
#     atoms = 0
#     bonds = 0
#     while True:
#         s = _read_block(session, stream)
#         if not s:
#             break
#         structures.append(s)
#         atoms += s.num_atoms
#         bonds += s.num_bonds
#     status = ("Opened mol2 file containing {} structures ({} atoms, {} bonds)".format
#               (len(structures), atoms, bonds))
#     return structures, status



def print_dict(dict):
    # print(s)
    for key, value in dict.items():
        print(key, ":", value,)
    print()


def _read_block(session, stream):
    """test docstring"""
    # First section should be commented out
    # Second section: "@<TRIPOS>MOLECULE"
    # Third section: "@<TRIPOS>ATOM"
    # Fourth section: "@<TRIPOS>BOND"
    # Fifth section: "@<TRIPOS>SUBSTRUCTURE"

    from numpy import (array, float64)
    from chimerax.core.atomic import AtomicStructure

    read_comments(session, stream)
    x = read_molecule(session, stream)
    read_atom(session, stream, int(x["num_atoms"]))
    read_bond(session, stream, int(x["num_bonds"]))
    read_substructure(session, stream)

    while len(stream.readline()) == 0:
        pass

    _read_block(session, stream)

    # s = AtomicStructure(session)


def read_comments(session, stream):

    import ast
    comment_dict = {}

    comment = stream.readline()
    while comment[0] == "#":
        line = comment.replace("#", "")
        parts = line.split(":")
        parts = [item.strip() for item in parts]
        if ":" not in line:
            for i in range(len(line), 1, -1):
                if line[i-1] == " ":
                    comment_dict[line[:i].strip()] = line[i:].strip()
                    break
        else:
            try:
                comment_dict[str(parts[0])] = ast.literal_eval(parts[1])

            except (ValueError, SyntaxError):
                comment_dict[str(parts[0])] = str(parts[1])

        comment = stream.readline()

    print_dict(comment_dict)

def read_molecule(sesson, stream):

    import ast
    while "@<TRIPOS>MOLECULE" not in stream.readline():
        pass
    molecular_dict = {}
    mol_lables = ["mol_name", ["num_atoms", "num_bonds", "num_subst", "num_feat", "num_sets"],\
    "mol_type", "charge_type", "status_bits"]

    for label in mol_lables:
        molecule_line = stream.readline().split()
        try:
            if all(isinstance(ast.literal_eval(item), int) for item in molecule_line):
                molecular_dict.update(dict(zip(label, molecule_line)))
        except (ValueError, SyntaxError):
            molecular_dict[label] = molecule_line[0]


    print_dict(molecular_dict)
    return molecular_dict


def read_atom(session, stream, atom_count):

    import ast
    while "@<TRIPOS>ATOM" not in stream.readline():
        pass


    atom_dict = {}

    for _ in range(atom_count):
        atom_line = stream.readline().strip()
        if len(atom_line) == 0:
            print("error: no line found")
        try:
            if isinstance(ast.literal_eval(atom_line[0]), int):
                pass
        except:
            print("error on line: ", atom_line)
            return None
        parts = atom_line.split()
        if len(parts) != 9:
            print("error: not enough entries on line: ", atom_line)
            return None
        # if not isinstance(int(parts[0]), int):
        #     print("error: first value is needs to be an integer")
        #     return None

        val_list = []
        atom_dict[int(parts[0])] = val_list
        for value in parts[1:]:
            try:
                val_list.append(ast.literal_eval(value))
            except (ValueError, SyntaxError):
                val_list.append(str(value))

    # PRINT TEST. DELETE LATER
    print_dict(atom_dict)

def read_bond(session, stream, bond_count):

    while "@<TRIPOS>BOND" not in stream.readline():
        pass

    bond_dict = {}

    for _ in range(bond_count):
        bond_line = stream.readline()
        parts = bond_line.split()
        if len(parts) != 4:
            print("error: not enough entries in under bond data")
        if not isinstance(int(parts[0]), int):
            print("error: first value is needs to be an integer")
            return None

        bond_dict[int(parts[0])] = parts[1:3]

    print_dict(bond_dict)

def read_substructure(session, stream):

    while "@<TRIPOS>SUBSTRUCTURE" not in stream.readline():
        pass



    substructure_dict = {}
    substructure_labels = ["subst_id", "subst_name", "root_atom", "subst_type",\
    "dict_type", "chain", "sub_type", "inter_bonds", "status", "comment" ]
    substructure_line = stream.readline().split()

    for _ in substructure_labels:
        substructure_dict.update(dict(zip(substructure_labels, substructure_line)))

    print_dict(substructure_dict)



# _read_block(None, open("ras.mol2", "r"))
_read_block(None, open("dock.mol2", "r"))


# note to self: try to ask if you can do a pip install package that would
# not disappear

exit()