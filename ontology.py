from owlready2 import *

onto = get_ontology("templates/ontology.owl").load()


def save_patents_to_ontology(patents_info):
    onto = get_ontology("templates/ontology.owl").load()
    for patent_info in patents_info:
        onto = patent_data_to_onto(onto, patent_info)

    onto.save("templates/result_all.owl")


def save_patent_to_ontology(patent_info):
    onto = get_ontology("templates/ontology.owl").load()
    onto = patent_data_to_onto(onto, patent_info)
    onto.save("templates/result.owl")


def patent_data_to_onto(onto, patent_info):
    device = onto.Device(patent_info['patentName'] + '_device_0')
    device.patentNumber = patent_info['patentNumber']
    device.patentName = patent_info['patentName']

    main_component = patent_info['mainComponent']
    device.conceptName = [main_component]

    if patent_info['problemName']:
        problem = onto.Problem(patent_info['patentName'] + '_problem')
        problem.problemName.append(patent_info['problemName'])
        device.solutionFor.append(problem)

    components = []
    temp_saos = patent_info['saos']
    
    for sao in temp_saos:
        if sao[0] not in components and sao[0] != main_component:
            components.append(sao[0])

        if sao[2] not in components and sao[2] != main_component:
            components.append(sao[2])

    saos_without_main = list(filter(lambda x: main_component != x[0], temp_saos))
    if patent_info['saos']:
        component_counter = 0

        entities = {}

        for comp in components:
            component = onto.Component(patent_info['patentName'] + '_component_' + str(component_counter))
            component.conceptName = [comp]
            component.partOf.append(device)

            entities[comp] = component
            component_counter = component_counter + 1
        
        for sao in saos_without_main:
            head = entities[sao[0]]
            dependent = entities[sao[2]]

            verb = sao[1]

            if verb in ['comprise']:
                head.comprises.append(dependent)
            
            if verb in ['consist', 'include']:
                head.consists.append(dependent)

            if verb in ['have']:
                head.parentFor.append(dependent)

            if verb in ['connect', 'attach']:
                head.connectedTo.append(dependent)

    return onto