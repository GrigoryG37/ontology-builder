import stanza
import text_processor as tp
import patent_processor as pp
import constants
import re
import string
import ontology as onto
from lxml import etree

nlp = stanza.Pipeline('en', processors='tokenize, mwt, pos, lemma, depparse')

def get_problem_text(patent_data):
    problem_text = get_problem_tags(patent_data)
    if problem_text:
        temp = '<?xml version="1.0" encoding="UTF-8"?><us-patent-grant>' + problem_text + '</us-patent-grant>'
        root = etree.fromstring(temp.encode('utf-8'))
        paragraphs = root.findall(".//p")
        if(paragraphs):
            paragraphs_without_tags = [''.join(paragraph.itertext()).strip() for paragraph in paragraphs]
            return paragraphs_without_tags
        else:
            return []
    else:
        return []


def get_problem_tags(patent_data):
    problem_pattern = 'Technical Problem</heading>'
    problem_index = patent_data.find(problem_pattern)
    if problem_index > -1:
        text_after_problem_heading = patent_data[problem_index + len(problem_pattern):]
        next_heading_index = text_after_problem_heading.find('<heading')
        problem_text = text_after_problem_heading[:next_heading_index]

        return problem_text

    return ''


def get_problem_sao(patent_content):
    problems = get_problem_text(patent_content)

    if problems:
        filtered_problems = list(filter(lambda problem: problem.find('present invention') > -1, problems))

        sao_problems = []
        for index, problem in enumerate(filtered_problems):
            tokens = tp.sentence_to_tokens(nlp, problem)
            if tp.is_any_solution_key_verb_there(tokens):
                key_verbs = tp.get_first_solution_key_verb(tokens)
                if key_verbs:
                    key_verb = key_verbs[0]
                    obj_root = tp.get_right_dependent_token(tokens, key_verb['id'])

                    # Выполнить поиск всех однородных
                    obj_roots = tp.get_all_homogeneous(tokens, obj_root)
                    obj_roots.insert(0, obj_root)
                    
                    for _obj in obj_roots:
                        sao_problems.append([key_verb['text'], tp.obj_tokens_to_str(tp.get_seq_for_object(tokens, _obj))])

                    for _obj in obj_roots:
                        _verb = tp.get_right_dependent_verb(tokens, _obj['id'])
                        if _verb:
                            curr_subj = _obj
                            curr_act = _verb
                            curr_obj = tp.get_right_dependent_token(tokens, curr_act['id'])

                            curr_objs = tp.get_all_homogeneous(tokens, obj_root)
                            curr_objs.insert(0, curr_obj)

                            subj_seq = tp.get_seq_for_object(tokens, curr_subj)
                            act_seq = tp.get_act_seq(tokens, _verb['id'])

                            obj = [tp.obj_tokens_to_str(tp.get_seq_for_object(tokens, obj_root)) for obj_root in curr_objs]
                            subj = tp.obj_tokens_to_str(subj_seq)
                            act = tp.obj_tokens_to_str(act_seq)
                            for obj_ in obj:
                                sao_problems.append([subj, act, obj_])
        return sao_problems
    else:
        return []


def prepare_segment(text):
    if text[-1] in string.punctuation:
        text = text[:-1] + '.'
    
    if text[-1].isalpha():
        text = text + '.'

    return text.capitalize()


def restore_segments(text):
    # Пока предполагаем, что всегда есть двоеточие
    restored_segments = []
    colon_index = tp.get_index_of_colon(text)
    left, right = tp.split_text_into_two_parts(text, colon_index, colon_index + 1)

    main_segment = left
    enumerated_segments = right.split(';')
    enumerated_segments = list(filter(lambda segment: segment, enumerated_segments))
    for enumerated_segment in enumerated_segments:
        if enumerated_segment.find(' and') > -1:
            # Издержки обработки. Предпоследний перечисляемый компонент может содержать and после точки с запятой
            # Нужно удалить его из начала сегмента

            restored_segments.append(f"{main_segment} {enumerated_segment.strip()}")
        else:
            restored_segments.append(f"{main_segment} {enumerated_segment.strip()}")

    #prepared_segments = [prepare_segment(segment) for segment in restored_segments]
    
    return restored_segments

def segmenation(text):
    segments = []
    text = text.replace('; and', ';')
    wherein_index = text.find('wherein')
    claims_without_wherein, wherein_claims = tp.split_text_into_two_parts(text, wherein_index, wherein_index + len('wherein'))

    segments_without_wherein = restore_segments(claims_without_wherein)
    segments_with_wherein = [segment.strip() for segment in wherein_claims.split('wherein')]

    segments = segments_without_wherein
    # Раскомментировать на случай, если будут анализироваться так же wherein
    #segments = segments_without_wherein + segments_with_wherein
    prepared_segments = [prepare_segment(segment) for segment in segments]

    return prepared_segments


def remove_article(text):
    result = re.sub(r'a |an |the ', '', text)
    return result

def get_main_component(tokens, priority_verb):
    root_token = tp.get_root_token(tokens)
    obj_root = None
    # Если ключевой глагол - рутовый, то необходимо искать слева субъект
    # # action - сам ключевой глагол
    if priority_verb['id'] == root_token['id']:
        act_root = priority_verb
        subj_root = tp.get_left_dependent_token(tokens, act_root['id'])

    # Рутовый токен - субъект, глагол - зависимое слово
    else:
        # Косяк извлечения, левое от глагола не всегда правильно определяется
        verb_head = tp.get_head_token(tokens, priority_verb['head'])
        if tp.is_verb(verb_head) and verb_head['lemma'] not in constants.key_verbs:
            return [], []

        if verb_head['deprel'] == 'nmod':
            subj_root = tp.get_head_token(tokens, verb_head['head'])
            act_root = priority_verb
            obj_root = verb_head
        else:
            # Получить зависимый глагол
            subj_root = root_token
            act_root = tp.get_right_dependent_verb(tokens, subj_root['id'])
            #print(act_root)

    # Теперь нужно извлечь объект
    if not obj_root:
        obj_root = tp.get_right_dependent_token(tokens, act_root['id'])

    # Выполнить поиск всех однородных
    obj_roots = tp.get_all_homogeneous(tokens, obj_root)
    obj_roots.insert(0, obj_root)

    # Сохранение
    act_lemma = act_root['lemma']
    subj_seq = tp.get_seq_for_object(tokens, subj_root)
    act_seq = tp.get_act_seq(tokens, act_root['id'])

    obj = [tp.obj_tokens_to_str(tp.get_seq_for_object(tokens, obj_root)) for obj_root in obj_roots]
    subj = tp.obj_tokens_to_str(subj_seq)
    act = tp.obj_tokens_to_str(act_seq)
    if act_lemma not in constants.key_verbs:
        return [], []
    else:
        return [subj, act, obj], [subj, act_lemma, obj]


def get_component(tokens, priority_verb):
    # Сначала определяется объект
    # Потом только субъект
    obj_root = tp.get_head_token(tokens, priority_verb['head'])

    # Косяк извлечения, левое от глагола не всегда правильно определяется
    if obj_root['deprel'] == 'nmod':
        subj_root = tp.get_head_token(tokens, obj_root['head'])
    elif tp.is_there_dependent_left(tokens, priority_verb['id']):
        # Получить левое зависимое слово
        subj_root = tp.get_left_dependent_token(tokens, priority_verb['id'])
    else:
        # Глагол является зависимым
        subj_root = tp.get_head_token(tokens, priority_verb['head'])

        # Выполнить поиск всех однородных
    obj_roots = tp.get_all_homogeneous(tokens, obj_root)
    obj_roots.insert(0, obj_root)

    act_root = priority_verb
    return [subj_root, act_root, obj_roots]


def extract_sao(patent_claim):
    segments = segmenation(tp.remove_claim_text_index_number(patent_claim))
    SAOs = []
    SAOs_with_lemma = []
    for segment in segments:
        current_saos = []
        current_saos_with_lemma = []
        tokens = tp.sentence_to_tokens(nlp, segment)

        # Если есть ключевые глаголы, то приступить к анализу
        if tp.is_any_key_verb_there(tokens):
            priority_verbs = tp.get_priority_verbs(tokens) # Ключевый глагол

            is_main_component_found = False
            while (priority_verbs):
                priority_verb = priority_verbs.pop(0)
                if not is_main_component_found:
                    main_component, main_component_with_lemma = get_main_component(tokens, priority_verb)
                    is_main_component_found = True

                    if main_component and main_component_with_lemma:
                        temp_saos = [[main_component[0], main_component[1], obj_comp] for obj_comp in main_component[2]]
                        temp_saos_with_lemma = [[main_component_with_lemma[0], main_component_with_lemma[1], obj_comp] for obj_comp in main_component_with_lemma[2]]
                        for temp_sao in temp_saos:
                            current_saos.append(temp_sao)

                        for temp_sao_with_lemma in temp_saos_with_lemma:
                            current_saos_with_lemma.append(temp_sao_with_lemma)
                else:
                    # Теперь выполнять поиск всех оставшихся токенов
                    # Получить самое лево существительное без зависимых слов до глагола
                    left_noun = tp.get_left_noun_without_dependencies(tokens, priority_verb['id'])
                    article_of_noun = tp.get_article_index_of_head(tokens, left_noun['id'])
                    #article_index = int(article_of_noun['id'])
                    if article_of_noun:
                        indexes = tp.get_token_indexes(article_of_noun)
                    else:
                        left_word = tp.get_left_dependent_token(tokens, left_noun['id'])
                        if left_word:
                            indexes = tp.get_token_indexes(left_word)
                        else:
                            indexes = tp.get_token_indexes(left_noun)

                    current_segment = segment[indexes[0]:]
                    curr_tokens = tp.sentence_to_tokens(nlp, current_segment)
                    p_verb = tp.get_priority_verb(curr_tokens)
                    curr_component, curr_component_with_lemma = get_main_component(curr_tokens, p_verb)
                    
                    if curr_component and curr_component_with_lemma:
                        temp_saos = [[curr_component[0], curr_component[1], obj_comp] for obj_comp in curr_component[2]]
                        temp_saos_with_lemma = [[curr_component_with_lemma[0], curr_component_with_lemma[1], obj_comp] for obj_comp in curr_component_with_lemma[2]]
                        for temp_sao in temp_saos:
                            current_saos.append(temp_sao)

                        for temp_sao_with_lemma in temp_saos_with_lemma:
                            current_saos_with_lemma.append(temp_sao_with_lemma)

        #print(current_saos)
        for current_sao in current_saos:
            SAOs.append(current_sao)

        for current_sao_with_lemma in current_saos_with_lemma:
            SAOs_with_lemma.append(current_sao_with_lemma)


        SAOs = [[remove_article(sao[0]), sao[1], remove_article(sao[2])] for sao in SAOs]
        SAOs_with_lemma = [[remove_article(sao[0]), sao[1], remove_article(sao[2])] for sao in SAOs_with_lemma]
    
    return SAOs, SAOs_with_lemma