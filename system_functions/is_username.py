def is_username(text: str):
    # если в тексте есть слово, начинающееся с @, возвращает это слово
    # в противном случае возвращает None
    text_list = text.strip().split()
    for word in text_list:
        if word[0] == '@':
            return word[1:]
    return None