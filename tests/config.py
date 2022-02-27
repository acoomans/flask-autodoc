import sys

# The way that the line number of a function is detected changed
# The old version chooses the location of the first decorator,
# the new version chooses the location of the 'def' keyword.
# We detect the version and support both.
NEW_FN_OFFSETS = sys.version_info >= (3, 8)
