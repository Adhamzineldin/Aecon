import datetime
from dateutil import parser
from django.contrib.auth import logout

class MyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
        
    def __call__(self, request):
        # Code to be executed for each request before the view (and later middleware) are called.
        try:
            session_creation = parser.parse(request.session['user_active_time'])
            time_diff =  datetime.datetime.now() - session_creation  
            time_diff = time_diff.total_seconds()
            time_diff = round(time_diff/60)
            print("time diff -", time_diff)
            if time_diff >= 60:
                del request.session['user_active_time']
                logout(request) 
            else:
                request.session['user_active_time'] = str(datetime.datetime.now())
                request.session.modified = True
        except Exception as e:
            request.session['user_active_time'] = str(datetime.datetime.now())
        response = self.get_response(request)
        # Code to be executed for each request/response after the view is called.
        return response
