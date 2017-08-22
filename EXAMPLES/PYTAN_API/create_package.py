#!/usr/bin/env python
"""
Create a package called package49
"""
# import the basic python packages we need
import os
import sys
import tempfile
import pprint
import traceback

# disable python from generating a .pyc file
sys.dont_write_bytecode = True

# change me to the path of pytan if this script is not running from EXAMPLES/PYTAN_API
pytan_loc = "~/gh/pytan"
pytan_static_path = os.path.join(os.path.expanduser(pytan_loc), 'lib')

# Determine our script name, script dir
my_file = os.path.abspath(sys.argv[0])
my_dir = os.path.dirname(my_file)

# try to automatically determine the pytan lib directory by assuming it is in '../../lib/'
parent_dir = os.path.dirname(my_dir)
pytan_root_dir = os.path.dirname(parent_dir)
lib_dir = os.path.join(pytan_root_dir, 'lib')

# add pytan_loc and lib_dir to the PYTHONPATH variable
path_adds = [lib_dir, pytan_static_path]
[sys.path.append(aa) for aa in path_adds if aa not in sys.path]

# import pytan
import pytan

# create a dictionary of arguments for the pytan handler
handler_args = {}

# establish our connection info for the Tanium Server
handler_args['username'] = "Administrator"
handler_args['password'] = "Tanium2015!"
handler_args['host'] = "10.0.1.240"
handler_args['port'] = "443"  # optional

# optional, level 0 is no output except warnings/errors
# level 1 through 12 are more and more verbose
handler_args['loglevel'] = 1

# optional, use a debug format for the logging output (uses two lines per log entry)
handler_args['debugformat'] = False

# optional, this saves all response objects to handler.session.ALL_REQUESTS_RESPONSES
# very useful for capturing the full exchange of XML requests and responses
handler_args['record_all_requests'] = True

# instantiate a handler using all of the arguments in the handler_args dictionary
print "...CALLING: pytan.handler() with args: {}".format(handler_args)
handler = pytan.Handler(**handler_args)

# print out the handler string
print "...OUTPUT: handler string: {}".format(handler)

# setup the arguments for the handler.delete() method
delete_kwargs = {}
delete_kwargs["objtype"] = u'package'
delete_kwargs["name"] = u'package49'

# setup the arguments for the handler() class
kwargs = {}
kwargs["expire_seconds"] = 1500
kwargs["display_name"] = u'package49 API test'
kwargs["name"] = u'package49'
kwargs["parameters_json_file"] = u'../../doc/example_of_all_package_parameters.json'
kwargs["verify_expire_seconds"] = 3600
kwargs["command"] = u'package49 $1 $2 $3 $4 $5 $6 $7 $8'
kwargs["file_urls"] = [u'3600::testing.vbs||https://content.tanium.com/files/initialcontent/bundles/2014-10-01_11-32-15-7844/custom_tagging_-_remove_tags_[non-windows]/CustomTagRemove.sh']
kwargs["local_files"] = [u'null_file.nil||0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef||77']
kwargs["verify_filter_options"] = [u'and']
kwargs["verify_filters"] = [u'Custom Tags, that contains:tag']
kwargs["command_timeout_seconds"] = 9999

# delete the object in case it already exists
# catch and print the exception error if it does not exist
print "...CALLING: handler.delete() with args: {}".format(delete_kwargs)
try:
    handler.delete(**delete_kwargs)
except Exception as e:
    print "...EXCEPTION: {}".format(e)

print "...CALLING: handler.create_package() with args: {}".format(kwargs)
response = handler.create_package(**kwargs)

print "...OUTPUT: Type of response: ", type(response)
print "...OUTPUT: print of response:"
print response

# call the export_obj() method to convert response to JSON and store it in out
export_kwargs = {}
export_kwargs['obj'] = response
export_kwargs['export_format'] = 'json'
print "...CALLING: handler.export_obj() with args {}".format(export_kwargs)
out = handler.export_obj(**export_kwargs)

# trim the output if it is more than 15 lines long
if len(out.splitlines()) > 15:
    out = out.splitlines()[0:15]
    out.append('..trimmed for brevity..')
    out = '\n'.join(out)

print "...OUTPUT: print the objects returned in JSON format:"
print out

# delete the object, we are done with it now
print "...CALLING: handler.delete() with args: {}".format(delete_kwargs)
delete_response = handler.delete(**delete_kwargs)

print "...OUTPUT: print the delete response"
print delete_response

'''STDOUT from running this:
...CALLING: pytan.handler() with args: {'username': 'Administrator', 'record_all_requests': True, 'loglevel': 1, 'debugformat': False, 'host': '10.0.1.240', 'password': 'Tanium2015!', 'port': '443'}
...OUTPUT: handler string: PyTan v2.1.4 Handler for Session to 10.0.1.240:443, Authenticated: True, Platform Version: 6.5.314.4301
...CALLING: handler.delete() with args: {'objtype': u'package', 'name': u'package49'}
...EXCEPTION: No results found searching for PackageSpec, name: u'package49' (error: Response command PackageNotFound does not match request command GetObject)!!
...CALLING: handler.create_package() with args: {'expire_seconds': 1500, 'display_name': u'package49 API test', 'name': u'package49', 'parameters_json_file': u'../doc/example_of_all_package_parameters.json', 'verify_expire_seconds': 3600, 'command': u'package49 $1 $2 $3 $4 $5 $6 $7 $8', 'file_urls': [u'3600::testing.vbs||https://content.tanium.com/files/initialcontent/bundles/2014-10-01_11-32-15-7844/custom_tagging_-_remove_tags_[non-windows]/CustomTagRemove.sh'], 'verify_filter_options': [u'and'], 'verify_filters': [u'Custom Tags, that contains:tag'], 'command_timeout_seconds': 9999}
...OUTPUT: Type of response:  <class 'taniumpy.object_types.package_spec.PackageSpec'>
...OUTPUT: print of response:
PackageSpec, name: 'package49', id: 95
...CALLING: handler.export_obj() with args {'export_format': 'json', 'obj': <taniumpy.object_types.package_spec.PackageSpec object at 0x102be8f90>}
...OUTPUT: print the objects returned in JSON format:
{
  "_type": "package_spec",
  "available_time": "1900-01-01T00:00:00",
  "command": "package49 $1 $2 $3 $4 $5 $6 $7 $8",
  "command_timeout": 9999,
  "creation_time": "2015-09-14T19:57:31",
  "deleted_flag": 0,
  "display_name": "package49 API test",
  "expire_seconds": 1500,
  "files": {
    "_type": "package_files",
    "file": [
      {
        "_type": "file",
        "bytes_downloaded": 0,
..trimmed for brevity..
...CALLING: handler.delete() with args: {'objtype': u'package', 'name': u'package49'}
...OUTPUT: print the delete response
[<taniumpy.object_types.package_spec.PackageSpec object at 0x102bd2b50>]

'''

'''STDERR from running this:

'''
