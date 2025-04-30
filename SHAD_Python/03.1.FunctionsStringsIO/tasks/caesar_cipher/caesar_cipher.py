import string


def caesar_encrypt(message: str, n: int) -> str:
    """Encrypt message using caesar cipher

    :param message: message to encrypt
    :param n: shift
    :return: encrypted message
    """
    n %= 26
    alph = ''.join(lower + upper for lower, upper in zip(string.ascii_lowercase, string.ascii_uppercase))
    return message.translate(str.maketrans(alph, alph[(n * 2):] + alph[:(n * 2)]))
