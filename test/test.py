import datetime
from yem import *

b = Book(title="Ex", pubdate=datetime.datetime.now(), x=datetime.date.today(), y=datetime.datetime.today().time())
b.author = ("pw", "jus", "lp")
for i in range(1, 20):
    ch = Chapter(title="Chapter " + str(i), text=Text.for_string("hello world"))
    b.append(ch)
    if i % 2 == 0:
        ch.append(Chapter(title=ch.title + ".1", text=Text.for_string("sub chapter")))

b.x = 222
print(make_book(b, r"D:\tmp", "pmab"))
