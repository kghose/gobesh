#OpenGL Tutorial 1 - Ian Mallett

#The documentation for   OpenGL: http://www.opengl.org/sdk/docs/man/
#The documentation for PyOpenGL: http://pyopengl.sourceforge.net/documentation/manual/
#The OpenGL documentation is more clear.

#In comments, I will refer to "PyOpenGL" as "OpenGL", but in reality, there is no
#OpenGL & Python, only PyOpenGL & Python.  Keep that in mind.  I will also write
#comments describing an operation, then place indented comments underneath each part,
#ex:

#Here is a comment about something:
#   Step 1 explanation
#   Step 2 explanation
#       Step 2, part 1 explanation
#       Step 2, part 2 explanation
#       Step 2, part 3 explanation
#   Step 3 explanation

#Now, on to the code!

#Imports
#   Import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
#   Import PyGame.
import pygame
from pygame.locals import *
#   Other Imports
import os, sys
import random
from math import *
#   Import my custom OpenGL Init. Module
import GL

#Center the Screen
if sys.platform == 'win32' or sys.platform == 'win64':
    os.environ['SDL_VIDEO_CENTERED'] = '1'

#Initialize PyGame
pygame.init()

#Make a PyGame Window
#   Screen Size
Screen = (800,600)
#   Set the Display Icon.  Here, I just make a blank icon,
#   and set that, because a "nothing" icon looks better than
#   the snake--mostly unrelated to OpenGL.   
icon = pygame.Surface((1,1)); icon.set_alpha(0); pygame.display.set_icon(icon)
#   Set the Caption on the Window
pygame.display.set_caption("[Program] - [Author] - [Version] - [Date]")
#   Create the Window.  These Flags tell SDL to let OpenGL
#   use the Window Surface for drawing.  
Surface = pygame.display.set_mode(Screen,OPENGL|DOUBLEBUF)
#   Now, Initialise OpenGL.  (See GL.pyw)
#       This sizes the viewport, and so on.
GL.resize(Screen)
#       This calls a whole bunch of functions that
#       are necessary to OpenGL, but are cluttery.
GL.init()

def GetInput():
    #Get the state of all of the keyboard buttons.
    key = pygame.key.get_pressed()
    #Get all the events.  If you click the "X" on the
    #window or press escape, close PyGame and quit.
    for event in pygame.event.get():
        if event.type == QUIT or key[K_ESCAPE]:
            pygame.quit(); sys.exit()
def Draw():
    #Clear Colours and Depth Buffer.
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    #This has the effect of clearing the screen.  One does
    #not draw over the previous frame, like in PyGame.
    
    #Reset the Cooridnate System ("Identity Matrix").
    #This "undos" all the transforms done by glTranslate()
    #and glRotate().  The origin is now again in the center
    #of you two-dimensional screen.  
    #glLoadIdentity()

    #Move 6 units into the Screen
    glTranslatef(.1*(random.random()-.5),.1*(random.random()-.5),1*(random.random()-.5))

    #Size the points to a visible size.  Normally, they are
    #one pixel big.  To enhance visibility, this makes them
    #larger.  Arguably, this doesn' have to be called every
    #frame, but repeating it doesn't hurt.
    glPointSize(5)

    #Begin drawing points
    glBegin(GL_POINTS)
    #Draw a point at the origin (now 5 units inside the screen)
    #glVertex3f(5*(random.random()-.5),5*(random.random()-.5),-30)
    glVertex3f(0,0,-30)
    #Done drawing points for now.
    glEnd()


    #Draw on Screen
    pygame.display.flip()
def main():
    #Main Loop
    while True:
        #Get the user's Input
        GetInput()
        #Draw
        Draw()
#Run the Program.
if __name__ == '__main__': main()

#You may have noticed that many of the functions look like *****f().
#The "f" means "float", and that function takes floats.  You CAN pass
#integers to a *****f() function, but you CANNOT pass floats to an
#integer function (these look like *****i()).  For the ease of using
#both types, integer and float, I simply use *****f() functions.
