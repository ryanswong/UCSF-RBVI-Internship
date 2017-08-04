# vim: set expandtab shiftwidth=4 softtabstop=4:



def open_mol2(session, stream, name):
    structures = []
    atoms = 0
    bonds = 0
    while True:
        s = _read_block(session, stream)
        if not s:
            break
        structures.append(s)
        atoms += s.num_atoms
        bonds += s.num_bonds
    status = ("Opened mol2 file containing {} structures {} atoms, {} bonds".format
              (len(structures), atoms, bonds))
    return structures, status


def _read_block(session, stream):
    """function that calls subfunctions that each read a specific section of the mol2 file"""
    # First section should be commented out
    # Second section: "@<TRIPOS>MOLECULE"
    # Third section: "@<TRIPOS>ATOM"
    # Fourth section: "@<TRIPOS>BOND"
    # Fifth section: "@<TRIPOS>SUBSTRUCTURE"

    from numpy import (array, float64)
    from chimerax.core.atomic import AtomicStructure

    comment_dict, molecular_dict = read_com_and_mol(session, stream)
    if not molecular_dict:
        return None
    atom_dict = read_atom(session, stream, int(molecular_dict["num_atoms"]))
    bond_dict = read_bond(session, stream, int(molecular_dict["num_bonds"]))
    substructure_dict = read_substructure(session, stream, int(molecular_dict["num_subst"])) #pass in # of substructures


    s = AtomicStructure(session)

    csd = build_residues(s, substructure_dict)
    cad = build_atoms(s, csd, atom_dict)
    build_bonds(s, cad, bond_dict)
    s.viewdock_comment = comment_dict

    return s


def read_com_and_mol(session, stream):
    """Parses commented section"""
    # import ast

    comment_dict = {}


    while True:
        comment = stream.readline()
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

    if comment == "@<TRIPOS>MOLECULE":
        pass
    else:
        molecule_line = stream.readline()

        while "@<TRIPOS>MOLECULE" not in molecule_line:
            if not molecule_line: #if not even "\n"
                return None, None
            molecule_line = stream.readline()

    molecular_dict = {}
    mol_labels = ["mol_name", ["num_atoms", "num_bonds", "num_subst", "num_feat", "num_sets"],\
    "mol_type", "charge_type", "status_bits"]


    for label in mol_labels:
        molecule_line = stream.readline().split()
        try:
            # Only for the integers (num_atoms, num_bonds, etc)
            if all(isinstance(int(item), int) for item in molecule_line):
                molecular_dict.update(dict(zip(label, molecule_line)))
        except (ValueError, SyntaxError):
            molecular_dict[label] = molecule_line[0]



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
        if len(parts) not in range(6, 11): # must be within 6-10 entries
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

def build_residues(s, substructure_dict):
    """ create chimeraX substructure dictionary (csd) """
    csd = {}
    # csd will be something like {"1": <residue>}

    for s_index in substructure_dict:


        # new_residue(self, residue_name, chain_id, pos, insert=' ')

        residue = s.new_residue(substructure_dict[s_index][0][:4], str(substructure_dict[s_index][5]), int(s_index))
        csd[s_index] = residue
    return csd


def build_atoms(s, csd, atom_dict):

    """ Creates chimeraX atom dictionary (cad)"""
    from numpy import array, float64

    cad = {}
    for key in atom_dict:
        name = atom_dict[key][0]
        element = atom_dict[key][4]
        if "." in element:
            split_element = element.split(".")
            element = split_element[0]
        xyz = [float(n) for n in atom_dict[key][1:4]]
        new_atom = s.new_atom(name, element)
        new_atom.coord = array(xyz, dtype=float64)
        # new_atom.serial_number = int(key)

        # adding ne atom to subst_id 
        csd[atom_dict[key][5]].add_atom(new_atom)

        cad[key] = new_atom

    return cad


def build_bonds(s, cad, bond_dict):
    for key in bond_dict:
        atom1index = bond_dict[key][0]
        atom2index = bond_dict[key][1]
        try:
            a1 = cad[atom1index]
            a2 = cad[atom2index]
        except KeyError:
            print("Error : bad atom index in bond")
        else:
            s.new_bond(a1, a2)
