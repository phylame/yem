import setpath
import yem

b = yem.Book(title="Ex")
b.author = ("pw", "jus", "lp")
for i in range(1, 20):
    ch = yem.Chapter(title="Chapter " + str(i), text=yem.Text.for_string("hello world"))
    b.append(ch)
    if i % 2 == 0:
        ch.append(yem.Chapter(title=ch.title + ".1", text=yem.Text.for_string("sub chapter")))
print(b)
print(yem.make_book(b, r"D:\tmp", "pmab"))
