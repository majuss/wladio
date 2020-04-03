import lirc
sockid = lirc.init("radio")

while True:
    codeIR = lirc.nextcode()
    if "up" in codeIR:
        print("UP")
        print(codeIR)
    if "down" in codeIR:
        print("DOWN")
        print(codeIR)
    if "next" in codeIR:
        print("NEXT")
        print(codeIR)
    if "prev" in codeIR:
        print("PREV")
        print(codeIR)
    if "menu" in codeIR:
        print("MENU")
        print(codeIR)
    if "play" in codeIR:
        print("PLAY")
        print(codeIR)