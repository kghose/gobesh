"""Some common imports."""

if sys.platform == "win32":
  # On Windows, the best timer is time.clock()
  default_timer = time.clock
else:
  # On most other platforms, the best timer is time.time()
  default_timer = time.time
