# vim: set expandtab shiftwidth=4 softtabstop=4:



def open_mol2(session, stream, name):
    structures = []
    atoms = 0
    bonds = 0
    while True:
        s = _read_block(session, stream)
        print(s)
        if not s:
            break
    #     structures.append(s)
    #     atoms += s.num_atoms
    #     bonds += s.num_bonds
    status = ("Opened mol2 file containing {} structures ({} atoms, {} bonds)".format
              (len(structures), 0, 0))
    return structures, status



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

    comment_dict = read_comments(session, stream)
    if not comment_dict:
        return None
    molecular_dict = read_molecule(session, stream)
    atom_dict = read_atom(session, stream, int(molecular_dict["num_atoms"]))
    bond_dict = read_bond(session, stream, int(molecular_dict["num_bonds"]))
    substructure_dict = read_substructure(session, stream) #pass in # of substructures

    print_dict(comment_dict)
    print_dict(molecular_dict)
    print_dict(atom_dict)
    print_dict(bond_dict)
    print_dict(substructure_dict)


    s = AtomicStructure(session)
    csd = build_residues(s, substructure_dict)
    cad = build_atoms(s, csd, atom_dict)
    # build_bonds(s, cad, bond_dict)

    return True

    # index2atom = {}
    # for n in range(0, len(molecular_dict["num_atoms"])):
    #         atom_index = int(parts[0])
    #         atom = s.newAtom(name, element)
    #         index2atom[atom_index] = atom




    # for _ in range(molecular_dict["num_bonds"]):
    #     a1 = index2atom[index1]
    #     a2 = index2atom[index2]
    #     s.newBond(a1, a2)

    # for _ in range(10):
    #     test_read = stream.readline().strip()
    #     print("test read: " , test_read)    



    return s


def read_comments(session, stream):
    """Parses commented section"""

    import ast
    comment_dict = {}


    while True:
        comment = stream.readline()
        # print("read comment:", (comment))

        if not comment:
            return None
        if not comment_dict and comment[0] == "\n":
            continue
        if comment[0] != "#" :
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
            try:
                comment_dict[str(parts[0])] = ast.literal_eval(parts[1])

            except (ValueError, SyntaxError):
                comment_dict[str(parts[0])] = str(parts[1])

        return comment_dict

def read_molecule(session, stream):
    """Parses molecule section"""

    import ast
    while "@<TRIPOS>MOLECULE" not in stream.readline():
        pass
    molecular_dict = {}
    mol_labels = ["mol_name", ["num_atoms", "num_bonds", "num_subst", "num_feat", "num_sets"],\
    "mol_type", "charge_type", "status_bits"]

    for label in mol_labels:
        molecule_line = stream.readline().split()
        try:
            if all(isinstance(ast.literal_eval(item), int) for item in molecule_line):
                molecular_dict.update(dict(zip(label, molecule_line)))
        except (ValueError, SyntaxError):
            molecular_dict[label] = molecule_line[0]


    return molecular_dict


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

        bond_dict[str(parts[0])] = parts[1:3]

    return bond_dict

def read_substructure(session, stream):
    """parses substructure section"""

    while "@<TRIPOS>SUBSTRUCTURE" not in stream.readline():
        pass

    substructure_dict = {}
    substructure_labels = ["subst_id", "subst_name", "root_atom", "subst_type",
    "dict_type", "chain", "sub_type", "inter_bonds", "status", "comment"]


    substructure_line = stream.readline().split()

    for _ in substructure_labels:
        substructure_dict.update(dict(zip(substructure_labels, substructure_line)))

    return substructure_dict

def build_residues(s, substructure_dict):
    #create new chimerax substructure dictionary
    csd = {}
    #csd will be something like {1: <residue>}

    for s_index in substructure_dict:
        residue = s.newResidue(substructure_dict[s_index][1],
        substructure_dict[s_index][2])
        csd.update({s_index : residue})
    return csd


def build_atoms(s, csd, atom_dict):
    cad = {}
    for key in atom_dict:
        name = atom_dict[key][0]
        element = atom_dict[key][4]
        if "." in element:
            split_element = element.split(".")
            element = split_element[0]
        new_atom = s.new_atom(name, element)
        cad.update({key : new_atom})

    return cad


def build_bonds(s, cad, bond_dict):
    for key in bond_dict:
        atom1 = bond_dict[key][0]
        atom2 = bond_dict[key][1]
        s.new_bond(atom1, atom2)






# ## TEST PURPOSE ONLY ####
# def test_run(file_name):
#     import os
#     file = os.path.join(os.getcwd(), 'example_files/{}'.format(file_name))
#     # print(open(file, "r").read())
#     with open(file, "r") as stream:
#         open_mol2(None, stream, file)
#
# test_run("ras.mol2")