with open("new.json", "r", encoding="utf-8") as f:
    my_code = f.read()

while True:
    repl = input("Введите, что изменить (или 0 для отмены): ")
    if repl == "0":
        break
    repl2 = input("Введите, на что заменить: ")
    my_code = my_code.replace(repl, repl2)
with open("bot.txt", "w", encoding="utf-8") as f:
    f.write(my_code)