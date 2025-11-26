
def remove_comment(text: str):
    mark = text.find("#")
    if mark != -1:
        return text[:mark]
    return text

def get_dat_cleaned_rows(text: str):
    lines = text.split("\n")
    cleaned_rows = filter(
        lambda x: len(x) != 0,
        map(
            lambda x: remove_comment(x).strip(),
            lines
        )
    )
    return cleaned_rows