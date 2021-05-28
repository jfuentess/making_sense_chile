## Python script to extract the interaction network among all school roles

import csv
import sys

import json

## Normalization of string names
def clear_string(s):
    s = s.strip() # Deleting spaces at the begining and end of the string
    s = s.split(" ")[0] # Extract only the first word
    return s

## Extract unique elements in a list
def unique(L): 
    # intilize a null list 
    unique_list = [] 
      
    # traverse for all elements 
    for x in L: 
        # check if exists in unique_list or not 
        if x not in unique_list: 
            unique_list.append(x) 

    return unique_list


## Transform code names to roles names
def vertex_name(str):
    if str == "PROFESOR_DE_AULA_EX":
        return "external\nclassroom\nteacher"
    elif str == 'PROFESOR_DE_AULA':
        return "classroom\nteacher"
    elif str == 'EDUCADOR_ESPECIAL':
        return 'special education\nteacher'
    elif str == 'SPECIAL_EDUCATION_TEACHER':
        return 'special education\nteacher'
    elif str  == "PROFESIONAL_DE_APOYO_AL_ESTUDIANTE":
        return "student support\nprofessional"
    elif str == "JEFE_DE_UTP":
        return "pedagogical-technical\ncoordinator"
    elif str == "OTHER":
        return "other"
    elif str == "COORDINADOR_ACADÉMICO_O_DE_CICLO":
        return "academic\ncoordinator"
    elif str == "MIEMBRO_DEL_EQUIPO_DE_GESTIÓN":
        return "management team\nmember"
    elif str == "APODERADO_O_FAMILIAR_E_UN_ESTUDIANTE":
        return "tutor"
    elif str == "ASISTENTE_DE_AULA":
        return "classroom\nassistant"
    elif str == "SPECIALIST_SUBJECT_TEACHER":
        return "specialist subject\nteacher"
    elif str == "ESTUDIANTE_DE_PEDAGOGÍA_EN_PRÁCTICA":
        return "trainee\nteacher"
    elif str == "GUARDIAN":
        return "legal\nguardian"
    elif str == "JEFE_DEPARTAMENTO":
        return "department\nhead"
    elif str == "INSPECTOR_DE_LA_ESCUELA":
        return "school\ninspector"
    elif str == "ASISTENTE_COORDINACION":
        return "management\nassistant"
    elif str == "PROFESIONAL_EXTERNO":
        return "external\nprofessional"
    elif str == "FAMILIA_PROFESOR":
        return "teacher\nfamily"
    elif str == "ESTUDIANTES":
        return "students"
    elif str == "FAMILIA_ESTUDIANTES":
        return "students\nfamily"
    elif str == "SCHOOL_PSYCHOLOGIST":
        return "Student support\nstaff"
    elif str == "PUPIL_ASSISTANT":
        return "teaching\nassistant"
    
    return str


def main():

    if len(sys.argv) != 4:
        print("Usage: python3 " + sys.argv[0] + " <log file> <roles file> <prefix output file>", file=sys.stderr)
        sys.exit(0)
        
    
    reg_file = sys.argv[1] # File with the log registers
    rol_file = sys.argv[2] # File with school roles    
    prefix_ofile = sys.argv[3] # Prefix path for the output files

    ## Dictionary of school roles
    dict_roles = {}

    # Loading the rol of each school member
    with open(rol_file, 'r') as read_obj:
        csv_reader = csv.DictReader(read_obj)

        # iterate over each line as a ordered dictionary
        for row in csv_reader:
            if row['ID'] in dict_roles:
                print("Repeated member " + row['iD'] + " in the file " + rol_file, file=sys.stderr)

            dict_roles[row['ID']] = row['ROL']


    schools = []
    relationship = []
    
    # Obtaining the different schools in the logs
    with open(reg_file, 'r') as read_obj:
        csv_reader = csv.DictReader(read_obj)
        for row in csv_reader:
            if not row['schoolCode']:
                print("Warning: registers without school code", file=sys.stderr)
            if row['schoolCode'] and row['schoolCode'] not in schools:
                schools.append(row['schoolCode'])

            if "TYPE_OF_INTERACTION" in row['log section']:
                interaction = clear_string(row['log text'])
                if interaction not in relationship:
                    relationship.append(interaction)

                       
    ## Getting the interaction network of each school
    ## Note: the implementation is inefficient, however it is enough for the
    ## context, since the number of registers is relative low 

    global_social_net = {}
    vertices_names = set()
    
    for school in schools:
        ## Interaction network per school
        social_net = {}
        for rel in relationship:
            social_net[rel] = {}

        interactions = 0
        # open file in read mode
        with open(reg_file, 'r') as read_obj:
            csv_reader = csv.DictReader(read_obj)

            # Source and target vertices in the interaction network
            src = ""
            tgt =""

            # iterate over each line as a ordered dictionary
            for row in csv_reader:
                if row['schoolCode'] == school:

                    if "ROLE" in row['log section']:
                        interactions = interactions + 1
                        src = dict_roles[row['ownerId']]
                        tgt = row['log text']

                        src = clear_string(src)
                        tgt = clear_string(tgt)

                        vertices_names.add(src)
                        vertices_names.add(tgt)
                        
                    if "TYPE_OF_INTERACTION" in row['log section']:
                        inter = clear_string(row['log text'])

                        if not src or not tgt:
                            print(" Warning: empty source or target", file=sys.stderr)
                            sys.exit(0)
                        
                        if src not in social_net[inter]:
                            social_net[inter][src] = {}

                        if tgt not in social_net[inter][src]:
                            social_net[inter][src][tgt] = 1
                        else:
                            social_net[inter][src][tgt] = int(social_net[inter][src][tgt]) + 1


            global_social_net[school] = social_net


    sort_vertices_names = list(vertices_names)
    sort_vertices_names.sort()
    
    for school in global_social_net.keys():
        ## Write output CSV (Edges of the interaction network)
        outf = open(prefix_ofile + "_edges_" + school + ".csv", 'w', newline ='')

        writer = csv.writer(outf, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow(["source", "target", "weight", "type"]) 

        node_ids = []
        for inter in global_social_net[school]:
            for src in global_social_net[school][inter]:
                ## We are interested in the social network of teachers
                if src != "PROFESOR_DE_AULA":
                    continue
                
                src_name = vertex_name(src)
                node_ids.append(src_name)
                for tgt in global_social_net[school][inter][src]:
                    tgt_name = vertex_name(tgt)
                    
                    writer.writerow([src_name, tgt_name,
                                     global_social_net[school][inter][src][tgt], 
                                     inter])
                    
                    node_ids.append(tgt_name)

        print("Total number of interactions in the School ", school, ": ", interactions)

        outf.close()


            
            
        ## Write output CSV (Nodes of the interaction network)
        outf = open(prefix_ofile + "_nodes_" + school + ".csv", 'w', newline ='')

        node_ids = unique(node_ids)
        writer = csv.writer(outf, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["name", "id"]) 

        i=0
        for vertex in sort_vertices_names:
            if vertex == "ASISTENTE_COORDINACION":
                continue
            elif vertex == "FAMILIA_ESTUDIANTES":
                continue
            v = vertex_name(vertex)
            writer.writerow([v, i]) 
            i = i+1
        outf.close()


if __name__ == "__main__":
    main()
