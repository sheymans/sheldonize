# We write our modal views here (Meetings, Tasks, etc)

from models import Meeting
from forms import MeetingForm
from braces.views import LoginRequiredMixin

# from django-fm
from fm.views import AjaxCreateView, AjaxUpdateView, AjaxDeleteView

class MeetingUpdateView(AjaxUpdateView, LoginRequiredMixin):
    form_class = MeetingForm
    model = Meeting
    pk_url_kwarg = 'meeting_pk'


