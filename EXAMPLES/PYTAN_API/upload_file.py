#!/usr/bin/env python
'''
Uploads a file to the Tanium Server. The term "upload" is used a bit loosely.
We are not starting with an existing file so the "uploaded" file is actually
being created on the Tanium Server from scratch.

Uploading files is a 2 step process. An accurate file size is needed for both
steps. (1) Get a new upload file id. (2) Send
file data in chunks to Tanium Server

To upload an existing file, additional functionality needs to be added to
read a file and break it into appropriate chunk sizes.

Recreating the upload functionality of the Tanium Console, file date should
be uploaded in 512K (524288 byte) chunks.

File data is bse64 encoded when sent to the server.
'''

# import the basic python packages we need
import os
import sys
import tempfile
import pprint
import traceback
import base64
import datetime

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
import taniumpy
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

# setup initial upload file data
chunk_size = 512 * 1024 # Change to a small value like '50' to see examples of uploading in multiple chunks
start_pos = 0
datetimeFormat = "%Y-%m-%d %H:%M:%S"
date_stamp = datetime.datetime.now().strftime(datetimeFormat)
upload_file_data = "I was uploaded with PyTan! How Cool is that?\nUpload Time: {}".format( date_stamp )
upload_file_size = len( upload_file_data )
upload_file_id = '-1'

# instantiate a handler using all of the arguments in the handler_args dictionary
print "...CALLING: pytan.handler() with args: {}".format(handler_args)
handler = pytan.Handler(**handler_args)

# print out the handler string
print "...OUTPUT: handler string: {}".format(handler)

# Step 1: Get new Upload File Id
print ""
print "==>Step 1: Requesting New Upload File Id"
uploadfile_kwargs = {}
uploadfile_kwargs["id"] = upload_file_id
uploadfile_kwargs["file_size"] = upload_file_size

upload_file_obj = taniumpy.UploadFile()
upload_file_obj.id = uploadfile_kwargs['id']
upload_file_obj.file_size = uploadfile_kwargs['file_size']

print "...CALLING: handler._upload with args: {}".format(uploadfile_kwargs)
response = handler._upload(upload_file_obj, **uploadfile_kwargs)
upload_file_id = response.id  # Update the upload_file_id with the new id returned by the server

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

# Step 2: Send file data to Tanium Server.
print ""
print "==>Step 2: Sending File Data to Tanium Server"
chunk_count = 1
for chunk_start_pos in range(0, upload_file_size, chunk_size):
        print "Uploading chunk #{}".format( chunk_count )
        chunk = upload_file_data[chunk_start_pos:chunk_start_pos+chunk_size]
        uploadfile_kwargs = { 'id' : upload_file_id
                            , 'file_size' : upload_file_size
                            , 'start_pos' : chunk_start_pos
                            , 'part_size' : len(chunk)
                            , 'bytes' : base64.b64encode( chunk )
                            }

        upload_file_obj = taniumpy.UploadFile()
        upload_file_obj.id = uploadfile_kwargs['id']
        upload_file_obj.file_size = uploadfile_kwargs['file_size']
        upload_file_obj.start_pos = uploadfile_kwargs['start_pos']
        upload_file_obj.part_size = uploadfile_kwargs['part_size']
        upload_file_obj.bytes = uploadfile_kwargs['bytes']

        print "...CALLING: handler._upload with args: {}".format(uploadfile_kwargs)
        response = handler._upload(upload_file_obj, **uploadfile_kwargs)

        print "...OUTPUT: Type of response: ", type(response)

        print "...OUTPUT: print of response:"
        print response

        #call the export_obj() method to convert response to JSON and store it in out
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

        chunk_count += 1

print ""
print "Uploaded file download URL: https://{}/cache/{}".format( handler_args['host'], response.destination_file )


'''STDOUT from running this:
...CALLING: pytan.handler() with args: {'username': 'Administrator', 'record_all_requests': True, 'loglevel': 1, 'debugformat': False, 'host': 'leela.planetexpress.loc', 'password': 'Tanium1', 'port': '443'}
...OUTPUT: handler string: PyTan v2.2.2 Handler for Session to leela.planetexpress.loc:443, Authenticated: True, Platform Version: 7.0.314.6319

==>Step 1: Requesting New Upload File Id
...CALLING: handler._upload with args: {'id': '-1', 'file_size': 77}
...OUTPUT: Type of response:  <class 'taniumpy.object_types.upload_file.UploadFile'>
...OUTPUT: print of response:
UploadFile, id: 2052768596
...CALLING: handler.export_obj() with args {'export_format': 'json', 'obj': <taniumpy.object_types.upload_file.UploadFile object at 0x10a069f10>}
...OUTPUT: print the objects returned in JSON format:
{
  "_type": "upload_file",
  "file_cached": 0,
  "id": 2052768596,
  "part_size": 0,
  "percent_complete": 0,
  "start_pos": 0
}

==>Step 2: Sending File Data to Tanium Server
Uploading chunk #1
...CALLING: handler._upload with args: {'bytes': 'SSB3YXMgdXBsb2FkZWQgd2l0aCBQeVRhbiEgSG93IENvb2wgaXMgdGhhdD8KVXBsb2FkIFRpbWU6IDIwMTctMDgtMjIgMTQ6MjA6Mzc=', 'part_size': 77, 'id': 2052768596, 'start_pos': 0, 'file_size': 77}
...OUTPUT: Type of response:  <class 'taniumpy.object_types.upload_file.UploadFile'>
...OUTPUT: print of response:
UploadFile, id: 2052768596
...CALLING: handler.export_obj() with args {'export_format': 'json', 'obj': <taniumpy.object_types.upload_file.UploadFile object at 0x10a069fd0>}
...OUTPUT: print the objects returned in JSON format:
{
  "_type": "upload_file",
  "destination_file": "e18c479ad5128cf900d0552352215d731d9173c082e5b03ecb20e59b8d69cdce",
  "file_cached": 1,
  "hash": "e18c479ad5128cf900d0552352215d731d9173c082e5b03ecb20e59b8d69cdce",
  "id": 2052768596,
  "part_size": 77,
  "percent_complete": 100,
  "start_pos": 0
}

Uploaded file download URL: https://10.0.1.240/cache/e18c479ad5128cf900d0552352215d731d9173c082e5b03ecb20e59b8d69cdce

'''

'''STDERR from running this:

'''
