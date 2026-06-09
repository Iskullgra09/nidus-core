from fastapi import Request


def get_request_language(request: Request) -> str:
    accept_lang = request.headers.get("accept-language", "en")
    return accept_lang.split(",")[0].split("-")[0].lower()
