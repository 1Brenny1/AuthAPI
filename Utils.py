from flask import make_response, Response
import random

def Format(Doc:str, **args) -> str:
    for key in args.keys():
        Doc = Doc.replace(f"{{{key}}}", str(args[key]))
    return Doc

def GenToken(length:int=50) -> str:
    Chars = "abcdefghijklmnopqrstuvwxyz1234567890!@$%^*()"
    Token = ""
    for i in range(length):
        Char = Chars[random.randint(0,len(Chars)-1)]
        if random.randint(0,1) == 1:
            Char = Char.upper()
        Token += Char
    return Token