# vim: set expandtab shiftwidth=4 softtabstop=4:


# def open_mol2(session, file, name):
#     structures = []
#     atoms = 0
#     bonds = 0
#     while True:
#         s = _read_block(session, file)
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

def loop(session, file):
    while not file:
        pass
    print("still going")
    # else:
    #     return None

    print(("_")*40)
    print("file type:", str(type(file)))
    print(("_")*40)
    print("printing file:", str(file))
    print(("_")*40)
    print()

    comment_dict = read_comments(session, file)
    molecule_dict = read_molecule(session, file)
    atom_dict = read_atom(session, file, int(molecule_dict["num_atoms"]))
    bond_dict = read_bond(session, file, int(molecule_dict["num_bonds"]))
    substructure_dict = read_substructure(session, file)
    print_dict(comment_dict)
    print_dict(molecule_dict)
    print_dict(atom_dict)
    print_dict(bond_dict)
    print_dict(substructure_dict)

    print(("_")*40)
    print("file type:", str(type(file)))
    print(("_")*40)
    print("printing file:", str(file))
    print(("_")*40)
    print()

    while True:
        loop(session, file)



def _read_block(session, stream):
    """fucntion that calls subfucntions that each read a specific section of the mol2 file"""
    # First section should be commented out
    # Second section: "@<TRIPOS>MOLECULE"
    # Third section: "@<TRIPOS>ATOM"
    # Fourth section: "@<TRIPOS>BOND"
    # Fifth section: "@<TRIPOS>SUBSTRUCTURE"

    # from numpy import (array, float64)
    # from chimerax.core.atomic import AtomicStructure

    # print(("_")*70)
    # print(type(stream))
    # print(("_")*70)
    # print(stream)
    # print(("_")*70)

    # with open(stream) as file:
    #     for line in file:
    #         print(line.strip())

    with open(stream) as file:

        loop(session, file)



        # for i in file:
        #     print(i)


        # print(("_")*40)
        # print("file type:", str(type(file)))
        # print(("_")*40)
        # print("printing file:", str(file))
        # print(("_")*40)
        # print()

        # comment_dict = read_comments(session, file)
        # molecule_dict = read_molecule(session, file)
        # atom_dict = read_atom(session, file, int(molecule_dict["num_atoms"]))
        # bond_dict = read_bond(session, file, int(molecule_dict["num_bonds"]))
        # substructure_dict = read_substructure(session, file)
        # print_dict(comment_dict)
        # print_dict(molecule_dict)
        # print_dict(atom_dict)
        # print_dict(bond_dict)
        # print_dict(substructure_dict)

        # print(("_")*40)
        # print("file type:", str(type(file)))
        # print(("_")*40)
        # print("printing file:", str(file))
        # print(("_")*40)
        # print()

        # _read_block(session, file)

    # test_read = file.readline().strip()
    # while not test_read:
    #     print('still reading: ', test_read)
    #     test_read = file.readline().strip()

    # for _ in range(2):
    #     test_read = file.readline().strip()
    #     print("test read:" , test_read)

    # print("test read: ", test_read)

    # hide:
    # index2atom = {}
    # for n in range(0, len(molecule_dict["num_atoms"])):
    #         atom_index = int(parts[0])
    #         atom = s.newAtom(name, element)
    #         index2atom[atom_index] = atom

    # for _ in range(molecule_dict["num_bonds"]):
    #     a1 = index2atom[index1]
    #     a2 = index2atom[index2]
    #     s.newBond(a1, a2)

    # counter = 0
    # while len(test_read) == 0:
    #     if test_read is None:
    #         print("TEST READ DONE")
    #         file.close()
    #     else:
    #         print("STILL READING...")
    # #     test_read = file.readline().strip()
    # # _read_block(session, file)
    # while len(test_read)

    # test_read = file.readline().strip()
    # _read_block(session, file)

    file.close()  # @HANNAH w/o this line, python won't stop running,
    # and thats why your mac overheated, especially
    # if you ran this file multiple times

    # s = AtomicStructure(session)


def read_comments(session, file):
    """Parses commented section"""

    # while



    import ast
    comment_dict = {}
    comment = file.readline()

    print("checkpoint1")

    if not comment:
        print("NO MOREL LINES!!!!")
        return None
    print("checkpoint2")
    print("comment:", comment)

    print("comment[0]:", comment[0])

    if not comment.strip():
        print("checkpoint2.5")

    while comment[0] == "#":
        print("checkpoint3")
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

        comment = file.readline()

    return comment_dict


def read_molecule(sesson, file):
    """Parses molecule section"""

    import ast
    while "@<TRIPOS>MOLECULE" not in file.readline():
        pass
    molecule_dict = {}

    mol_lables = ["mol_name", ["num_atoms", "num_bonds", "num_subst", "num_feat", "num_sets"],
                  "mol_type", "charge_type", "status_bits"]

    for label in mol_lables:
        molecule_line = file.readline().split()  # becomes a list
        try:
            if all(isinstance(ast.literal_eval(item), int) for item in molecule_line):
                molecule_dict.update(dict(zip(label, molecule_line)))
        except (ValueError, SyntaxError):
            molecule_dict[label] = molecule_line[0]

    return molecule_dict


def read_atom(session, file, atom_count):
    """parses atom section"""

    import ast
    while "@<TRIPOS>ATOM" not in file.readline():
        pass

    atom_dict = {}

    for _ in range(atom_count):
        atom_line = file.readline().strip()
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
        atom_dict[str(parts[0])] = val_list
        for value in parts[1:]:
            try:
                val_list.append(ast.literal_eval(value))
            except (ValueError, SyntaxError):
                val_list.append(str(value))

    # PRINT TEST. DELETE LATER
    return atom_dict


def read_bond(session, file, bond_count):
    """parses bond section"""

    while "@<TRIPOS>BOND" not in file.readline():
        pass

    bond_dict = {}

    for _ in range(bond_count):
        bond_line = file.readline()
        parts = bond_line.split()
        if len(parts) != 4:
            print("error: not enough entries in under bond data")
        if not isinstance(int(parts[0]), int):
            print("error: first value is needs to be an integer")
            return None

        bond_dict[str(parts[0])] = parts[1:3]

    return bond_dict


def read_substructure(session, file):
    """parses substructure section"""

    while "@<TRIPOS>SUBSTRUCTURE" not in file.readline():
        pass

    substructure_dict = {}
    substructure_labels = ["subst_id", "subst_name", "root_atom", "subst_type",
                           "dict_type", "chain", "sub_type", "inter_bonds", "status", "comment"]

    substructure_line = file.readline().split()  # becomes a list

    for _ in substructure_labels:
        substructure_dict.update(
            dict(zip(substructure_labels, substructure_line)))

    return substructure_dict


### TEST PURPOSE ONLY ####
def test_run(file_name):
    import os
    file = os.path.join(os.getcwd(), 'example_files/{}'.format(file_name))
    # print(open(file, "r").read())
    _read_block(None, file)

test_run("ras(short).mol2")
