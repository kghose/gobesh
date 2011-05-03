import BaseHTTPServer
import time
import cgi

HOST_NAME = '' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 8888 # Maybe set this to 9000.
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def do_HEAD(s):
    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()
  def do_GET(s):
    """Respond to a GET request."""
    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()
    s.wfile.write("<html><head><title>Title goes here.</title></head>")
    s.wfile.write("<body><p>This is a test.</p>")
    # If someone went to "http://something.somewhere.net/foo/bar/",
    # then s.path equals "/foo/bar/".
    s.wfile.write("<p>You accessed path: %s</p>" % s.path)
    s.wfile.write(
      """<form name="input" action="html_form_action.asp" method="POST">
Username: <input type="text" name="user" />
<input type="submit" value="Submit" />
</form>""")
    s.wfile.write("</body></html>")

  def do_POST(self):
    # Parse the form data posted
    form = cgi.FieldStorage(
        fp=self.rfile, 
        headers=self.headers,
        environ={'REQUEST_METHOD':'POST',
                 'CONTENT_TYPE':self.headers['Content-Type'],
                 })

    # Begin the response
    self.send_response(200)
    self.end_headers()
    self.wfile.write('Client: %s\n' % str(self.client_address))
    self.wfile.write('Path: %s\n' % self.path)
    self.wfile.write('Form data:\n')

    # Echo back information about what was posted in the form
    for field in form.keys():
        field_item = form[field]
        if field_item.filename:
            # The field contains an uploaded file
            file_data = field_item.file.read()
            file_len = len(file_data)
            del file_data
            self.wfile.write('\tUploaded %s (%d bytes)\n' % (field, 
                                                             file_len))
        else:
            # Regular form value
            self.wfile.write('\t%s=%s\n' % (field, form[field].value))
    return

if __name__ == '__main__':
  server_class = BaseHTTPServer.HTTPServer
  httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
  print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
  try:
      httpd.serve_forever()
  except KeyboardInterrupt:
      pass
  httpd.server_close()
  print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)

