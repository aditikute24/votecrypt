from django import forms
from django.core.cache import cache

class NewPoll(forms.Form):
    question = forms.CharField(label = 'Question', widget = forms.TextInput(attrs = {'class':'form-control form-control-lg'}))
    option_1 = forms.CharField(label = 'Option 1', widget = forms.TextInput(attrs = {'class':'form-control form-control-lg'}))
    option_2 = forms.CharField(label = 'Option 2', widget = forms.TextInput(attrs = {'class':'form-control form-control-lg'}))

    def __init__(self, *args, **kwargs):
        #print "Entered init"
        # #self.request = kwargs.pop('request', None)
        super(NewPoll, self).__init__(*args, **kwargs)
        #if self.request:	
        i = cache.get('extra_fields')
        if i:
            #print i
            for e in range(0, i):
                name = 'option_{}'.format(e + 3)
                #print (name)
                self.base_fields[name] = self.fields[name] = forms.CharField(label = 'Option {}'.format(e + 3), widget = forms.TextInput(attrs = {'class':'form-control form-control-lg'}))

            #print (self)
            #self.fields['test2'] = forms.CharField(required = False)
            print ("Added")

    class Meta:
        fields = '__all__'


class BlankForm(forms.Form):
    #question = forms.CharField(label = 'Question', widget = forms.TextInput(attrs = {'class':'form-control form-control-lg'}))

    
    class Meta:
        fields = '__all__'