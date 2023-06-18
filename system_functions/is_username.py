def is_username(text: str):
    # if in text is word started with @ return this word
    # else returns None
    text_list = text.strip().split()
    username = None
    for word in text_list[1:]:
        username = word.startswith('@')
    return username
