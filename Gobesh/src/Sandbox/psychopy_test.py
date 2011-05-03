from psychopy import visual, core #import some libraries from PsychoPy

mywin = visual.Window([800,600],monitor="testMonitor", units="deg") #create a window

#create some stimuli
grating = visual.PatchStim(win=mywin, mask="circle", size=3, pos=[-4,0], sf=3)
fixation = visual.PatchStim(win=mywin, size=0.5, pos=[0,0], sf=0, rgb=-1)

#draw the stimuli and update the window
grating.draw()
fixation.draw()
mywin.update()

#pause, so you get a chance to see it!
core.wait(5.0)
