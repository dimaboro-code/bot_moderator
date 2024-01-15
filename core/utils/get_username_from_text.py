def is_username(text: str):
    # если в тексте есть слово, начинающееся с @, возвращает это слово
    # в противном случае возвращает None
    text_list = text.strip().split()
    for word in text_list:
        if word[0] == '@':
            return word[1:]
    return None


def get_status_from_text(text: str):
    # в противном случае возвращает None
    text_list = text.strip().split()
    for index, word in enumerate(text_list):
        if word == 'Статус:':
            return text_list[index + 1] + ' ' + text_list[index + 2]
    return None
