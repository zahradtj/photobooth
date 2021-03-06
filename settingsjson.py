import json

settings_json = json.dumps([
    {'type': 'title',
     'title': 'Event Information'},
    {'type': 'string',
     'title': 'Event Name',
     'desc': 'Enter event name',
     'section': 'event',
     'key': 'title'},
    {'type': 'title',
     'title': 'Email'},
    {'type': 'string',
     'title': 'Email Address',
     'desc': 'Enter email address',
     'section': 'email',
     'key': 'username'},
    {'type': 'password',
     'title': 'Email Password',
     'desc': 'Enter email password',
     'section': 'email',
     'key': 'password'},
    {'type': 'string',
     'title': 'Email Subject',
     'desc': 'Enter email subject',
     'section': 'email',
     'key': 'subject'},
    {'type': 'string',
     'title': 'Email Body',
     'desc': 'Enter email body',
     'section': 'email',
     'key': 'body'},
    {'type': 'title',
     'title': 'Photos'},
    {'type': 'filepath',
     'title': 'Photo Headers',
     'desc': 'Choose a photo header',
     'section': 'photos',
     'key': 'selected_header'},
    {'type': 'numeric',
     'title': 'Number of Photos',
     'desc': 'Enter max number of photos per session',
     'section': 'photos',
     'key': 'max'},
    {'type': 'title',
     'title': 'Prints'},
    {'type': 'numeric',
     'title': 'Number of Prints',
     'desc': 'Enter max number of prints per session',
     'section': 'prints',
     'key': 'max'}])
