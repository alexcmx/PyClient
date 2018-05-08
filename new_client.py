import asyncio
import yaml
from msvcrt import *
from tkinter import *
from threading import Thread
import queue
import time
f = True
root = None
q=queue.Queue()
reader,writer = None, None
f2= False
def client(q):

    async def tcp_client(loop):
        global f
        global root
        global reader
        global writer
        reader, writer = await asyncio.open_connection('127.0.0.1', 4444 , loop=loop)

        '''login'''

        while True:
            nick = input("Nickname: ")
            password = input("Password: ")
            data = {nick:password}
            writer.write(('login ' + yaml.dump(data)+'\x0c').encode())
            data = await reader.readuntil(separator='\x0c'.encode())
            data = data.decode()
            if data =="logon successful\x0c":
                f = False
                break
            else:
                print(data[:-1]+ " Try again")


        '''2 Streams. One - reading from server. Second - waiting from combination to enter'''

    async def reading_from_server(q):
        while True:
            if f:
                await asyncio.sleep(1)
            else:
                break

        while True:
            data = await reader.readuntil(separator=b'\x0c')
            """work with data"""
            decoded_data = data.decode()
            q.put(decoded_data)
            while not f2:
                pass
            global root
            root.event_generate('<<Data-Recieved>>')

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    tasks= [loop.create_task(tcp_client(loop)), loop.create_task(reading_from_server(q))]
    wait_tasks = asyncio.wait(tasks)
    loop.run_until_complete(wait_tasks)
    loop.close()


def interface(q):
    global f2
    global root
    root = Tk()
    root.title("Клиент v 1.0")
    f2= True
    global writer
    root.geometry("800x600")
    def send():
        msg = text.get('1.0', END)
        whom = people.curselection()
        writer.write(("msg " + yaml.dump((people.get(whom), msg)) + '\x0c').encode())
        time.sleep(.1)
        writer.write(("dialog " + people.get(whom) + '\x0c').encode())

    def dialog(event):
        whom = people.curselection()
        writer.write(("dialog "+ people.get(whom) + '\x0c').encode())

    def new_data(event):
        data = q.get()
        if data.startswith("msgs"):
            """got msgs with someone"""
            msgvar.set(data[5:-1])

            """use msgs"""
        elif data.startswith("msg "):
            """"you've got new message from ...."""
            msg = """You've got new message from """ + data[4:]
            """use as label"""
            alrm.set(msg)
            def text_destroy():
                time.sleep(1)
                alrm.set("")
            """destroys frame after 5 sec"""
            t = Thread(target=text_destroy)
            t.start()
            whom = people.curselection()
            data_ = people.get(whom)
            if data_==data[4:]:
                writer.write(("dialog " + data_).encode())
            """update dialog if msg was on it"""
        elif data.startswith("people"):
            ppl = yaml.load(data[7:-1])
            people.delete(0,END)
            if len(ppl)>0:
                for i in ppl:
                    people.insert(END, i)


    #msgsFrame = Frame(root, height=60, width= 80,bg='green',bd=5)
    buttonFrame = Frame(root, width=25,height=5)
    alarmFrame = Frame(root,  width=25,height=5)
    alrm=StringVar()
    alarm = Label(alarmFrame, textvariable= alrm)
    text = Text(root,height= 10, width = 80, font='Arial 8', wrap=WORD)
    msgvar = StringVar()
    msgs = Label(root,height=60, width= 80, textvariable=msgvar, font='Arial 10')
    msgvar.set("Some Text")
    people = Listbox(root, height=40, width= 30, selectmode=SINGLE)
    button = Button(buttonFrame, text="Send", command=send)

    people.pack(side='left')
    #peopleFrame.pack(side='left')

    alarmFrame.pack(side='bottom')
    alarm.pack()
    buttonFrame.pack(side='bottom')
    #textFrame.pack(side= 'bottom')

    text.pack(side='bottom')
    """Your message """

    #msgsFrame.pack(side= 'top')
    """dialog """
    msgs.pack(side='top')

    """online """
    people.pack()

    button.pack()
    people.bind("<Double-Button-1>", dialog)
    root.bind('<<Data-Recieved>>', new_data)
    root.mainloop()

t = Thread(target=interface, args=(q,))
t2 = Thread(target=client, args=(q,))
t2.start()
while True:
    if f==False:
        t.start()
        break


"""делаем 3 функции async def первая устанавливает соединение логинится и заканчивает работу а остальне две ждут ответа от сервера и ждут нажатия кнопки пользователем"""


"""...... PROFITTTTTTTTTTTTTTTTTt"""