from django.forms import ModelForm, save_instance
from models import UserOptIn


class OptInForm(ModelForm):
    class Meta:
        model = UserOptIn
        fields = ['feature']

    def __init__(self, *args, **kwargs):
        self.should_enable=True
        self.user=None
        if 'enabled' in kwargs:
            self.should_enable = kwargs['enabled']
            del kwargs['enabled']
        if 'user' in kwargs:
            self.user = kwargs['user']
            del kwargs['user']

        super(OptInForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        if self.instance.pk is None:
            fail_message = 'created'
        else:
            fail_message = 'changed'
        self.instance.user = self.user
        self.instance.enabled = self.should_enable
        return save_instance(self, self.instance, ['feature','user','enabled'],
                             fail_message, commit, construct=False)