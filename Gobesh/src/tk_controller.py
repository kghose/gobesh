#!/usr/local/bin/python     
from Tkinter import *       

from multiprocessing.connection import Client

class Application(Frame):              
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid(padx=10,pady=10)
        address = ('localhost', 6000)
        try:
          self.conn = Client(address, authkey='gobesh controller')
        except:
          Message(self, text="Server not running", bg='white',
                  fg='white', relief=GROOVE).pack(padx=10, pady=10)
          self.quit()
         
        self.createWidgets()

    def createWidgets(self):
        self.goButton = Button ( self, text='Go',
            command=self.button_go )        
        self.goButton.grid(row=0)

        self.abortButton = Button ( self, text='Abort',
            command=self.button_abort )        
        self.abortButton.grid(column=1,row=0)

        self.quitButton = Button ( self, text='Quit',
            command=self.button_quit )        
        self.quitButton.grid(column=2,row=0)
    
    def button_go(self):
      self.conn.send('go')
      
    def button_abort(self):
      self.conn.send('abort')
          
    def button_quit(self):
      self.conn.send('quit')
        
app = Application()                    
app.master.title("Gobesh") 
app.mainloop()  