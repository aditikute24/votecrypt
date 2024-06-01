from django.views.generic import FormView, TemplateView, ListView, View
from .forms import *
from django.urls import reverse_lazy
from utility.blinders import *
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from utility.wallet import Wallet

class Home(TemplateView):
    template_name = 'home.html'
    hashed_blinded_secret = None
    signed_blinded_secret = None
    signed_unblinded_secret = None
    tip_message = "Choose Vaidate Option to Get Started."

    def get(self, request, *args, **kwargs):
        self.hashed_blinded_secret = self.request.COOKIES.get('hashed_blinded_secret')
        ##print ("Got" + str(self.hashed_blinded_secret))

        self.signed_blinded_secret = self.request.COOKIES.get('signed_blinded_secret')
        self.signed_unblinded_secret = self.request.COOKIES.get('signed_unblinded_secret')

        try:
            self.signed_blinded_secret = HashedBlindedSecret.objects.get(hashed_blinded_secret = self.hashed_blinded_secret).signed_secret
            #response.set_cookie('signed_blinded_secret', self.signed_blinded_secret, max_age = 365*24*60*60) #one year
            self.request.session['signed_blinded_secret'] = self.signed_blinded_secret
            #print ("Try worked !", self.signed_blinded_secret)
        except:
            pass

        '''if self.hashed_blinded_secret and self.signed_blinded_secret and not self.signed_unblinded_secret:
            #print ("Chali gayuu!!")
            #print (self.hashed_blinded_secret)
            #print (self.signed_blinded_secret)
            #print (self.signed_unblinded_secret)'''

        return super(Home, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        if self.request.COOKIES.get('signed_unblinded_secret') or self.request.session.get('unblinded_signed'):
            kwargs['enter_poll'] = True
            self.tip_message = "Validation Complete. Ready to Enter the Poll!"
        else:
            try:
                if self.request.session.get('signed_blinded_secret') or self.request.COOKIES.get('signed_blinded_secret'):
                    self.signed_blinded_secret = self.request.session.get('signed_blinded_secret')
                    #self.signed_blinded_secret = HashedBlindedSecret.objects.get(hashed_blinded_secret = self.hashed_blinded_secret).signed_secret
                    self.tip_message = "Authority signature successful. Ready to generate Unblinded Key."
                    kwargs['hide_validate'] = True
                if self.request.session.get('hashed_blinded_secret') or self.request.COOKIES.get('hashed_blinded_secret'):
                    self.tip_message = "Waiting for authority to sign the hashed_blinded_secret."
                    kwargs['disable_validate'] = True
            except:
                pass
                '''if self.request.session.get('hashed_blinded_secret') or self.request.COOKIES.get('hashed_blinded_secret'):
                    self.tip_message = "Waiting for authority to sign the hashed_blinded_secret."
                    kwargs['disable_validate'] = True'''
                    

        
        kwargs['tip_message'] = self.tip_message
        return super(Home, self).get_context_data(**kwargs)

    def render_to_response(self, context, **response_kwargs):
        response = super(Home, self).render_to_response(context, **response_kwargs)
        if self.request.session.get('unblinded_signed'):
            #print ("Entrd if")
            self.signed_unblinded_secret = self.request.session.get('unblinded_signed')
            #print (self.signed_unblinded_secret)
            response.set_cookie('signed_unblinded_secret', self.signed_unblinded_secret, max_age = 365*24*60*60) #one year
            #print ("co " + str(self.request.COOKIES.get('signed_unblinded_secret')))
            del(self.request.session['unblinded_signed'])
        if self.request.session.get('hashed_blinded_secret'):
            self.hashed_blinded_secret = self.request.session.get('hashed_blinded_secret')
            response.set_cookie('hashed_blinded_secret', self.hashed_blinded_secret, max_age = 365*24*60*60) #one year
            del(self.request.session['hashed_blinded_secret'])
            ##print (self.request.COOKIES.get('hashed_blinded_secret'))
        if self.request.session.get('signed_blinded_secret'):
            self.signed_blinded_secret = self.request.session.get('signed_blinded_secret')
            response.set_cookie('signed_blinded_secret', self.signed_blinded_secret, max_age = 365*24*60*60) #one year

        
        '''try:
            self.signed_blinded_secret = HashedBlindedSecret.objects.get(hashed_blinded_secret = self.hashed_blinded_secret).signed_secret
            response.set_cookie('signed_blinded_secret', self.signed_blinded_secret, max_age = 365*24*60*60) #one year
            self.request.session['signed_blinded_secret'] = self.signed_blinded_secret
            #print ("Try worked !", self.signed_blinded_secret)
        except:
            pass'''
        
        return response


class AuthHome(LoginRequiredMixin, TemplateView):
    template_name = 'auth_home.html'
    redirect_field_name = None


class BlindToValidate(FormView):
    form_class = BlindToValidate
    template_name = 'blindtovalidate.html'
    success_url = reverse_lazy('home')
    binded_secret = None

    def post(self, request, *args, **kwargs):        
        form = self.get_form()
        if form.is_valid():
            ##print ("valid")
            ##print (form.cleaned_data)

            secret_message = form.cleaned_data['secret_id']
            secret_number = int(form.cleaned_data['secret_number'])

            self.blinded_secret = get_blinded_secret(secret_message, secret_number)
            ##print (self.blinded_secret)
            messages.add_message(self.request, messages.SUCCESS, 'The generated blinded_secret is: \n{}'.format(self.blinded_secret))
            self.request.session['hashed_blinded_secret'] = self.blinded_secret
            #signed_blinded_secret = get_signed_blinded_secret(blinded_secret)
            obj, created = HashedBlindedSecret.objects.get_or_create(hashed_blinded_secret = self.blinded_secret)

            #obj.hashed_blinded_secret = self.blinded_secret
            obj.save()

        return super(BlindToValidate, self).post(request, *args, **kwargs)


class NewValidation(ListView):
    model = HashedBlindedSecret
    template_name = 'new_validations.html'
    context_object_name = 'blinded_secrets'

    def get_queryset(self):
        return HashedBlindedSecret.objects.filter(is_signed = False)


    

class Login(LoginView):
    template_name = 'login.html'
    
    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        form = form_class(**self.get_form_kwargs())

        form.fields['username'] = forms.CharField(label = 'Username', widget = forms.TextInput(attrs = {'required':'required', 'class':'form-control form-control-lg'}))
        form.fields['password'] = forms.CharField(label = 'Password', widget = forms.PasswordInput(attrs = {'required':'required', 'class':'form-control form-control-lg'}))
        ##print (form.base_fields)

        return form


class SignBlinded(View):

    def get(self, request, *args, **kwargs):
        ##print ("this" + self.kwargs['hashed_blinded_secret'])

        hashed_blinded_secret = self.kwargs['hashed_blinded_secret']
        signed_blinded_secret = get_signed_blinded_secret(hashed_blinded_secret)

        obj = HashedBlindedSecret.objects.get(hashed_blinded_secret = hashed_blinded_secret)
        obj.signed_secret = signed_blinded_secret
        obj.is_signed = True
        obj.save()

        messages.add_message(self.request, messages.SUCCESS, 'The generated signed_blinded_secret is: \n{}'.format(signed_blinded_secret))

        return redirect('node:new_validations')


class UnblindSigned(FormView):
    signed_unblinded_secret = None
    template_name = 'signedtounblind.html'
    form_class = SignedUnblindForm
    success_url = reverse_lazy('home')
    #tip_message = ""

    def get(self, request, *args, **kwargs):
        messages.add_message(self.request, messages.SUCCESS, 'The signed_blinded_secret is: \n{}'.format(self.request.COOKIES.get('signed_blinded_secret')))

        return super(UnblindSigned, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            ##print ("valid")
            ##print (form.cleaned_data)

            secret_number = int(form.cleaned_data['secret_number'])

            self.signed_unblinded_secret = get_unblinded_secret(self.request.COOKIES.get('signed_blinded_secret'), secret_number)
            self.request.session['unblinded_signed'] = self.signed_unblinded_secret

            obj = HashedBlindedSecret.objects.get(hashed_blinded_secret = self.request.COOKIES.get('hashed_blinded_secret'))
            obj.unblinded_signed_secret = self.signed_unblinded_secret
            obj.save()

            #print (self.signed_unblinded_secret)

            messages.add_message(self.request, messages.SUCCESS, 'The unblinded_signed_secret is: \n{}'.format(self.signed_unblinded_secret))

        return super(UnblindSigned, self).post(request, *args, **kwargs)
        

    '''def render_to_response(self, context, **response_kwargs):
        response = super(UnblindSigned, self).render_to_response(context, **response_kwargs)
        if self.request.session.get('unblinded_signed'):
            #print ("Entrd if")
            self.signed_unblinded_secret = self.request.session.get('unblinded_signed')
            #print (self.signed_unblinded_secret)
            response.set_cookie('signed_unblinded_secret', self.signed_unblinded_secret, max_age = 365*24*60*60) #one year
            #print ("co " + str(self.request.COOKIES.get('signed_unblinded_secret')))
            del(self.request.session['unblinded_signed'])
        
        return response'''


class Verify(FormView):
    signed_unblinded_secret = None
    template_name = 'verify_login.html'
    form_class = VerifyLogin
    success_url = reverse_lazy('poll:poll_home')

    def get(self, request, *args, **kwargs):
        self.signed_unblinded_secret = self.request.COOKIES.get('signed_unblinded_secret')
        messages.add_message(self.request, messages.SUCCESS, 'The unblinded_signed_secret is: \n{}'.format(self.signed_unblinded_secret))

        return super(Verify, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():

            secret_string = form.cleaned_data['secret_id']
            if verify_signature(secret_string, self.request.COOKIES.get('signed_unblinded_secret')):
                #print ("Success")
                wallet_obj = Wallet(self.request.COOKIES.get('signed_unblinded_secret')[0:6])
                if wallet_obj.load_keys():                    
                    print ("Loaded", wallet_obj.public_key)
                else:
                    wallet_obj.create_keys()
                    wallet_obj.save_keys()
                    ##print ("created", wallet_obj.public_key)
                self.request.session['public_key'] = wallet_obj.public_key
            else:
                form.add_error('secret_id', 'Signature Validation Failed!')
                #messages.add_message(self.request, messages.ERROR, 'Signature Validation Failed!')        
                return self.form_invalid(form)

        return super(Verify, self).post(request, *args, **kwargs)



    


    
