import mdetect

class PreviousURLMiddleware(object):
    """
    Make sure to remember current and previous url, but ignoring eventfeed and ajax as they are internal.
    We use that to when saving and deleting tasks to go back to the previous view.
    """
    def process_response(self, request, response):
        if response.status_code == 200 and request.user.is_authenticated():
            visiting_url = request.get_full_path()
            if 'current_url' in request.session:
                old_current = request.session['current_url']
            else:
                old_current = False

            request.session['current_url'] = visiting_url

            # only update previous when old_current is OK though:
            forbidden_terms = ["eventfeed", "ajax", "modal" ]
            if old_current:
                matching_forbidden_terms = filter(lambda term: term in old_current, forbidden_terms)
                print "matching: ", matching_forbidden_terms
            else:
                matching_forbidden_terms = []

            # also when the current has numbers, it is not OK (that's task
            # details, we don't want to go back there)
            # page has a number usually also but that's fine (task/meeting
            # details are not fine)
            if old_current and not matching_forbidden_terms and ("page" in old_current or not any(char.isdigit() for char in old_current)):
                request.session['previous_url'] = old_current

        print "previous: ", request.session['previous_url']
        print "current: ", request.session['current_url']
        return response


class DetectMobile:
    def process_request(self, request):
        user_agent = request.META.get("HTTP_USER_AGENT")
        http_accept = request.META.get("HTTP_ACCEPT")
        if user_agent and http_accept:
            agent = mdetect.UAgentInfo(userAgent=user_agent, httpAccept=http_accept)
            request.mobile_esp_agent = agent   # in case we want more information about the device
            if agent.detectMobileQuick():
                request.device_type = 'mobile'
            elif agent.detectTierTablet():
                request.device_type = 'tablet'
            else:
                request.device_type = 'desktop'
        else:
            request.mobile_esp_agent = None
            request.device_type = 'desktop'   # default
