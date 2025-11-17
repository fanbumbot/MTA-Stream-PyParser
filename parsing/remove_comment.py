
def remove_comment(text: str):
    mark = text.find("#")
    if mark != -1:
        return text[:mark]
    return text