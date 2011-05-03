"""A collection of dummy event modules created for the purpose of testing.
The """

class FakeSubjectEyeXY:
  """An event module that supplies x,y data pretending to be an ernest 
  experimental subject"""
  def __init__(self):
    self.sample_rate = 1000 #interpreted as Hz
    self.polling_interval = 10 #interpreted as ms
    self.last_polled_timestamp = None
    
  
  def startup(self, common_data = {}):
    """This function is called once at the start of the experiment.
    common variables used:
    'sample rate' - floating point. Interpreted as Hz
    'polling interval' - integer, interpreted as ms. Will return data when this
                         amount of time has passed between polls
    common variables written:
    NONE"""
    print 'Starting up %s' %(self.__class__.__name__)
    self.sample_rate = common_data['sample rate']
    self.polling_interval = common_data['polling interval']
    
  def poll(self, common_data = {}, timestamp=None):
    """
    common variables read:
    'fake subject params' -> (a dict)
        'target xy' - a tuple indicating where the subject should look
        'target p' - float [0,1] governing with what success the subject should
                    look towards the target
        'movement mode' - 'saccade' or 'smooth pursuit' depending on what you
                           want the subject to do
        'transform matrix' - a 2x3 list that carries the desired transform 
                             matrix for the eye position data
    'eye position' -> (a dict)
        'transform matrix' - a 2x3 list for the current transform matrix to 
                             convert the raw input to degrees
    common variables written:
    'eye position' -> (a dict)
        'eye x' - a list of floats interpreted as degrees
        'eye y' - a list of floats interpreted as degrees
        'last timestamp' - a float interpreted wrt to the main loop timestamp
                           indicating when the last time stamp was 
    """
    
    
    
    
  def shutdown(self, common_data = {}):
    """This function is called once when the experiment is quitting."""
    print 'Shutting down %s' %(self.__class__.__name__)
