def open_mol2(session, stream, name):
    structures = []
    atoms = 0
    bonds = 0
    while True:
        s = _read_block(session, stream)
        # print(s)
        if not s:
            break
        # structures.append(s)
        # atoms += s.num_atoms
        # bonds += s.num_bonds
    # status = ("Opened mol2 file containing {} structures ({} atoms, {} bonds)".format
    #           (len(structures), atoms, bonds))
    # return structures, status



def print_dict(dict):
    # print(s)
    for key, value in dict.items():
        print(key, ":", value,)
    print()


def _read_block(session, stream):
    """function that calls subfunctions that each read a specific section of the mol2 file"""
    # First section should be commented out
    # Second section: "@<TRIPOS>MOLECULE"
    # Third section: "@<TRIPOS>ATOM"
    # Fourth section: "@<TRIPOS>BOND"
    # Fifth section: "@<TRIPOS>SUBSTRUCTURE"

    from numpy import (array, float64)
    from chimerax.core.atomic import AtomicStructure

    # print("TEST1")

    comment_dict , molecular_dict= read_com_and_mol(session, stream)
    if not molecular_dict:
        return None
    print_dict(comment_dict)
    print_dict(molecular_dict)


    atom_dict = read_atom(session, stream, int(molecular_dict["num_atoms"]))
    print_dict(atom_dict)


    bond_dict = read_bond(session, stream, int(molecular_dict["num_bonds"]))
    print_dict(bond_dict)


    # substructure_dict = read_substructure(session, stream, int(molecular_dict["num_subst"])) #pass in # of substructures
    # print_dict(substructure_dict)


    print()
    print("########")
    print("success")
    print("########")
    print()


    return True


def read_com_and_mol(session, stream):
    """Parses commented section"""
    # import ast

    comment_dict = {}


    # Comment section

    while True:
        comment = stream.readline()
        # print(comment)
        if not comment: 
            break
        if not comment_dict and comment[0] == "\n": #before the comment section
            continue
        if comment[0] != "#":  #for the end of comment section
            break
        line = comment.replace("#", "")
        parts = line.split(":")
        parts = [item.strip() for item in parts]
        if ":" not in line:
            for i in range(len(line), 1, -1):
                if line[i-1] == " ":
                    comment_dict[line[:i].strip()] = line[i:].strip()
                    break
        else:
            comment_dict[(parts[0])] = parts[1]

    # print("CHECKPOINT1")

    # Molecule section

    if comment == "@<TRIPOS>MOLECULE":
        pass
    else:
        molecule_line = stream.readline()

        while "@<TRIPOS>MOLECULE" not in molecule_line:
            if not molecule_line: #if it's not even "\n".  is true if at the end of a file
                return None, None
            molecule_line = stream.readline()

    # return comment_dict, None

    molecular_dict = {}
    mol_labels = ["mol_name", ["num_atoms", "num_bonds", "num_subst", "num_feat", "num_sets"],\
    "mol_type", "charge_type", "status_bits"]

    line_num = 0


    for label in mol_labels:
        line_num += 1
        # print("line_num: ", line_num)
        if line_num == 1:
            molecule_line = stream.readline().strip()
            while not molecule_line:
                molecule_line = stream.readline().strip()
            molecular_dict[label] = molecule_line
            continue
        

        # Only for the integers (num_atoms, num_bonds, etc)
        if line_num == 2:
            molecule_line = stream.readline().split()
            if all(isinstance(int(item), int) for item in molecule_line):
                molecular_dict.update(dict(zip(label, molecule_line)))
            else:
                raise ValueError("Second line needs to be series of integers")
            
        else:
            molecule_line = stream.readline().strip()
            molecular_dict[label] = molecule_line
        if "@<TRIPOS>ATOM" in molecule_line:
            break

    return comment_dict, molecular_dict


def read_atom(session, stream, atom_count):
    """parses atom section"""

    import ast
    while "@<TRIPOS>ATOM" not in stream.readline():
        pass


    atom_dict = {}

    for _ in range(atom_count):
        atom_line = stream.readline().strip()
        if len(atom_line) == 0:
            print("error: no line found")
        parts = atom_line.split()
        # parts wil be like, ['1', 'C1', 9.4819, 36.0139, 21.8847, 'C.3', 1, 'RIBOSE_MONOPHOSPHATE', 0.0767]
        if len(parts) != 9:
            print("error: not enough entries on line: ", atom_line)
            return None

        atom_dict[(parts[0])] = parts[1:]


    # atom_dict would now be: 
    # {1 : ['C1', '9.4819', '36.0139', '21.8847', 'C.3', '1', 'RIBOSE_MONOPHOSPHATE', '0.0767'],
    # 2 : ['C2'....] }

    return atom_dict

def read_bond(session, stream, bond_count):
    """parses bond section"""

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

        bond_dict[parts[0]] = parts[1:3]

    return bond_dict

def read_substructure(session, stream, num_subst):
    """parses substructure section"""

    while "@<TRIPOS>SUBSTRUCTURE" not in stream.readline():
        pass

    for _ in range(num_subst):
        substructure_dict = {}
        subst_line = stream.readline()
        parts = subst_line.split()

        substructure_dict[parts[0]] = parts[1:]

    return substructure_dict


# ## TEST PURPOSE ONLY ####
def test_run(file_name):
    import os
    file = os.path.join(os.getcwd(), 'example_files/{}'.format(file_name))
    # print(open(file, "r").read())
    with open(file, "r") as stream:
        open_mol2(None, stream, file)


test_run("poses(short).mol2")
# test_run("ras(short).mol2")





















