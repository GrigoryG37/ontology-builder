import constants
import re

def text_to_tokens(pipeline, text):
    """Преобразование входного текста в токены."""
    doc = pipeline(text)
    return doc.to_dict()


def sentence_to_tokens(pipeline, text):
    """Преобразование входного предложения в токены."""
    return text_to_tokens(pipeline, text)[0]


def get_index_of_colon(text):
    """Получить индекс двоеточия."""
    return text.find(':')


def get_index_of_semicolon(text):
    """Получить индекс точки с запятой."""
    return text.find(';')


def is_wherein_in_beginning(text):
    """Есть ли в начале описания."""
    result = re.findall(r'^wherein|claim \d+, wherein', text)
    if result:
        return True
    
    return False


def get_first_key_verb(tokens):
    """Получить ключевые глаголы среди токенов."""
    return list(filter(lambda token: token['upos'] == constants.verb and token['lemma'] in constants.key_verbs, tokens))


def get_all_homogeneous(tokens, root_token):
    """Получить все однородные члены."""
    conj_tokens = get_all_conj_tokens(tokens, root_token['id'])
    #appos_tokens = tp.get_all_appos_tokens(tokens, root_token['id']) # Бывает, что однородный член почему-то считается уточнением
    #return appos_tokens + conj_tokens
    return conj_tokens


def get_first_solution_key_verb(tokens):
    """Получить ключевые глаголы среди токенов."""
    return list(filter(lambda token: token['upos'] == constants.verb and token['lemma'] in constants.key_solution_verbs, tokens))


def is_there_dependent_right(tokens, token_id):
    """Проверить, есть ли зависимые слова справа у токена."""
    return any(list(filter(lambda token: token['head'] == int(token_id) and int(token['id']) > int(token_id), tokens)))


def is_there_dependent_left(tokens, token_id):
    """Проверить, есть ли зависимые слова слева у токена."""
    return any(list(filter(lambda token: token['head'] == int(token_id) and int(token['id']) < int(token_id) and token['upos'] == constants.noun, tokens)))


def get_all_conj_tokens(tokens, token_id):
    """Получить все токены с типом связи - conj для токена с token_id."""
    return list(filter(lambda token: token['deprel'] == 'conj' and token['head'] == int(token_id) and int(token['id']) > int(token_id), tokens))


def get_all_appos_tokens(tokens, token_id):
    """Получить все токены с типом связи - appos для токена с token_id."""
    return list(filter(lambda token: token['deprel'] == 'appos' and token['head'] == int(token_id) and int(token['id']) > int(token_id), tokens))


def is_segmentation_required(text):
    """Требуется ли сегментация текста."""
    if is_there_semicolon(text) and not is_semicolon_last_symbol(text):
        return True

    if text.find(',') != -1:
        return True

    return False


def is_any_key_verb_there(tokens):
    """Есть ли хоть один ключевой глагол в тексте."""
    verbs = list(filter(lambda _token: _token['upos'] == constants.verb, tokens))
    return any(token['lemma'] in constants.key_verbs for token in verbs)


def is_any_solution_key_verb_there(tokens):
    """Есть ли хоть один ключевой глагол в тексте для проблема-решение."""
    verbs = list(filter(lambda _token: _token['upos'] == constants.verb, tokens))
    return any(token['lemma'] in constants.key_verbs for token in verbs)



def is_there_colon(text):
    """Проверяет, есть ли двоеточие в тексте."""
    if get_index_of_colon(text) == -1:
        return False

    return True


def is_colon_last_symbol(text):
    """Является ли двоеточие последним символов в строке."""
    index = get_index_of_colon(text)
    
    if index == len(text) - 1:
        return True

    return False


def is_there_semicolon(text):
    """Проверяет, есть ли точка с запятой в тексте."""
    if text.find(';') == -1:
        return False

    return True


def is_there_wherein(text):
    """Проверяет, есть ли wherein в тексте."""
    if text.find('wherein') == -1:
        return False
    
    return True


def is_there_comma(text):
    """Проверяет, есть ли запятая в тексте."""
    if text.find(',') == -1:
        return False

    return True


def is_semicolon_last_symbol(text):
    """Является ли точка с запятой последним символов в строке."""
    index = text.find(';')
    
    if index == len(text) - 1:
        return True

    return False


def is_verb_part_of_object(tokens, verb_id):
    """Является ли отглагольное словообразование частью описания объекта."""
    return verb_id != 1 and tokens[verb_id - 2]['upos'] == constants.article


def is_root_last(tokens, root_id):
    """Root токен является последним в предложении."""
    return root_id == len(tokens)


def get_head_token(tokens, head_id):
    """Получить главное слово."""
    return list(filter(lambda token: token['id'] == str(head_id), tokens))[0]


def get_dependent_token(tokens, token_id):
    """Получить зависимое слово."""
    return list(filter(lambda token: token['head'] == int(token_id), tokens))


def get_left_dependent_token(tokens, token_id):
    """Получить зависимое слово слева от главного."""
    dependent_tokens = list(filter(lambda token: token['head'] == int(token_id) and int(token['id']) < int(token_id), tokens))
    if dependent_tokens:
        return dependent_tokens[0]

    return None


def get_left_noun_without_dependencies(tokens, token_id):
    left_nouns = list(filter(lambda token: int(token['id']) < int(token_id) and token['upos'] == constants.noun, tokens))
    if left_nouns:
        return left_nouns[-1]
    
    return None


def get_right_dependent_token(tokens, token_id):
    """Получить зависимое слово справа от главного."""
    dependent_tokens = list(filter(lambda token: token['head'] == int(token_id) and int(token['id']) > int(token_id), tokens))
    if dependent_tokens:
        return dependent_tokens[0]

    return None


def get_right_dependent_verb(tokens, token_id):
    """Получить зависимое слово справа от главного."""
    dependent_tokens = list(filter(lambda token: token['head'] == int(token_id) and int(token['id']) > int(token_id) and is_verb(token), tokens))
    if dependent_tokens:
        return dependent_tokens[0]

    return None


def get_main_act(tokens, token_id):
    """Получить зависимый глагол."""
    return list(filter(lambda token: token['head'] == int(token_id) and is_verb(token) and token['id'] > token_id, tokens))[0]


def get_act_seq(tokens, token_id):
    aux_token = list(filter(lambda token: token['deprel'] == 'aux' and token['head'] == int(token_id), tokens))
    advmod_token = list(filter(lambda token: token['deprel'] == 'advmod' and token['head'] == int(token_id), tokens))
    start_tokens = aux_token + advmod_token

    if start_tokens:
        index = int(start_tokens[0]['id'])

        return tokens[index - 1:int(token_id)]

    return [tokens[int(token_id) - 1]]


def get_root_token(tokens):
    """Получить root токен."""
    return list(filter(lambda token: token['head'] == 0, tokens))[0]


def get_article_index_of_head(tokens, head_id):
    """Получить артикль"""
    res = list(filter(lambda token: token['head'] == int(head_id) and is_required_pos(token, constants.article), tokens))
    if res:
        return res[0]

    return None 


def get_seq_for_object(tokens, obj_root):
    """Получить описание объекта/субъекта целиком в виде токенов."""
    obj_id = int(obj_root['id'])
    if get_article_index_of_head(tokens, obj_root['id']):
        article_id = int(get_article_index_of_head(tokens, obj_root['id'])['id'])
        return tokens[article_id - 1:obj_id]
    else:
        return tokens[obj_id - 1:obj_id]

def obj_tokens_to_str(tokens):
    """Преобразовать последовательность токенов субъекта/объекта в строку."""
    return ' '.join([token['text'] for token in tokens]).lower()


def is_required_pos(token, upos):
    """Является ли токен требуемой частью речи."""
    return token['upos'] == upos


def is_there_required_pos(tokens, upos):
    """Имеется ли в списке токенов слово требуемой части речи."""
    return any(is_required_pos(token, upos) for token in tokens)


def is_verb(token):
    """Является ли токен глаголом или отглагольным словообразованием."""
    #return token['upos'] == constants.verb
    return is_required_pos(token, constants.verb)


def is_cconj(token):
    """Является ли токен союзом."""
    return is_required_pos(token, constants.cconj)


def is_noun(token):
    """Является ли токен существительным."""
    return is_required_pos(token, constants.noun)


def is_there_verb(tokens):
    """Имеется ли в списке токенов глагол или отглагольное словообразование."""
    return any(is_verb(token) for token in tokens)


def is_there_homogeneous(tokens):
    """"Имеются ли в предложении однородные члены"""
    return is_there_required_pos(tokens, constants.cconj)


def is_there_comprise(tokens):
    """Есть ли глагол, начальная форма которого - comprise."""
    return any(token['lemma'] in constants.verbs for token in tokens)

def get_tokens_by_xpos(tokens, xpos):
    """Получить токены по соответствующему значению xpos."""
    return list(filter(lambda token: token['xpos'] == xpos, tokens))


def get_tokens_by_xpos_list(tokens, xpos_list):
    """Получить токены c xpos, входящими в список необходимых xpos."""
    return list(filter(lambda token: token['xpos'] in xpos_list, tokens))


def get_priority_verb2(tokens):
    """Получить наиболее приоритетный глагол."""
    verbs = get_tokens_by_xpos_list(tokens, constants.verbs)
    vbp_tokens = get_tokens_by_xpos(verbs, 'VBP')
    vbz_tokens = get_tokens_by_xpos(verbs, 'VBZ')
    vbn_tokens = get_tokens_by_xpos(verbs, 'VBN')
    vbg_tokens = get_tokens_by_xpos(verbs, 'VBG')
    vbx_tokens = vbp_tokens + vbz_tokens + vbg_tokens + vbn_tokens
    vbx_tokens = list(filter(lambda token: token['lemma'] in constants.key_verbs, vbx_tokens))
    return vbx_tokens[0]


def get_priority_verb(tokens):
    """Получить список ключевых глаголов в тексте."""
    return list(filter(lambda token: token['upos'] == constants.verb and token['lemma'] in constants.key_verbs, tokens))[0]


def get_priority_verbs(tokens):
    """Получить список ключевых глаголов в тексте."""
    return list(filter(lambda token: token['upos'] == constants.verb and token['lemma'] in constants.key_verbs, tokens))


def get_index_of_verb(tokens):
    """Получить индекс первого глагола или отглагольного словообразования."""
    verbs = list(filter(lambda token: is_verb(token), tokens))
    if len(verbs):
        return verbs[0]["id"]

    return -1


def get_token_indexes(token):
    """Получить начальный и конечный индексы слова в тексте."""
    indexes = token["misc"].split("|")
    return [int(extract_index_from_misc_string(index)) for index in indexes]


def extract_index_from_misc_string(misc_string):
    """Извлечь индекс символа."""
    index_of_symbol = misc_string.find("=")
    return misc_string[index_of_symbol + 1:]


def split_text_into_two_parts(text, end, start):
    """Разделить предложение на две части."""

    # TODO: Дать нормальное название входным параметрам

    left = get_left_side(text, end)
    right = get_right_side(text, start)
    return left, right


def get_left_side(text, end):
    """Получить левую часть строки."""
    return text[:end].rstrip()


def get_right_side(text, start):
    """Получить правую часть строки."""
    return text[start:].lstrip()


def is_claim_text_with_index(text):
    """Проверить, есть ли у claim-text индекс компонента."""
    dot_index = text.find(".")
    return text[:dot_index].isnumeric()


def remove_claim_text_index_number(text):
    """Удалить порядковый номер из начала строки"""
    dot_index = text.find(".")
    return text[dot_index + 1:].lstrip()
