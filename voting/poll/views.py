from django.views.generic import FormView, View, TemplateView
from .forms import *
from django.core.cache import cache
from django.shortcuts import redirect
from django.http import HttpResponse
from django.urls import reverse_lazy, reverse
import pickle
from collections import OrderedDict
from django.conf import settings
import os
from django import forms
from django.contrib import messages
from utility.transaction import Transaction
from utility.wallet import Wallet
from utility.blockchain import Blockchain
from django.contrib.auth.mixins import LoginRequiredMixin

def read_file():
    try:
        location = os.path.join(settings.BASE_DIR, 'poll/poll.ovs')
        with open(location, mode = 'rb') as f:  
            #print ("Entered read")   
            file_contents = pickle.loads(f.read())
            #self.file_contents = pickle.loads(f.read())
            #print ("Read " + str(file_contents))
            f.close()

            return file_contents

        """if file_contents:
            print ("hai")
        else:
            print ("blank")"""
        
    except:
        print ("Except")
        pass


def write_file(file_contents):
    try:
        location = os.path.join(settings.BASE_DIR, 'poll/poll.ovs')
        with open(location, mode = 'wb') as f:
            f.write(pickle.dumps(file_contents))
            f.close()

        
    except:
        print ("Except")
        pass


class CreatePoll(LoginRequiredMixin, FormView):
    template_name = 'new_question.html'
    form_class = NewPoll
    success_url = reverse_lazy('node:auth_home')
    polls = []
    file_contents = None
    redirect_field_name = None
    

    def post(self, request, *args, **kwargs):
        this_poll = []
        form = NewPoll(request.POST)
        #print (form)
        i = 1
        

        '''try:
            location = os.path.join(settings.BASE_DIR, 'poll/poll.ovs')
            with open(location, mode = 'rb') as f:  
                print ("Entered read")   
                self.file_contents = pickle.loads(f.read())
                #self.file_contents = pickle.loads(f.read())
                print ("Read " + str(self.file_contents))
                f.close()

            """if file_contents:
                print ("hai")
            else:
                print ("blank")"""
            
        except:
            print ("Except")
            pass'''

        self.file_contents = read_file()
        #print ("Function test" + str(self.file_contents))

        if form.is_valid():
            for field in form.cleaned_data:
                #print (field)

                if field == 'question':
                    this_poll.append((self.file_contents['length'] + 1, form.cleaned_data[field], ['active']))
                else:
                    this_poll.append((i, form.cleaned_data[field]))
                    i += 1
        #print (this_poll)
        #print ("Here " + str(self.file_contents))
        self.file_contents['polls'].append(this_poll)
        self.file_contents['length'] += 1

        print ("FC " + str(self.file_contents))

        write_file(self.file_contents)

        messages.add_message(self.request, messages.SUCCESS, "Poll Created Successfully!")
        

        '''try:
            location = os.path.join(settings.BASE_DIR, 'poll/poll.ovs')
            with open(location, mode = 'wb') as f:
                f.write(pickle.dumps(self.file_contents))
                f.close()

            
        except:
            print ("Except")
            pass'''

        return super(CreatePoll, self).post(request, *args, **kwargs)


class AddOption(View):

    def get(self, request, *args, **kwargs):
        print ("entered add option")
        if cache.get("extra_fields"):
            cache.set("extra_fields", cache.get("extra_fields") + 1, 21600)
        else:
            cache.set("extra_fields", 1, 21600)
        print ("Cache is " + str(cache.get('extra_fields')))
        #return reverse("poll:new_question")

        return redirect('poll:new_question')


class PollHome(TemplateView):
    template_name = 'questions_list.html'
    file_contents = None
    active_questions_list = []
    inactive_questions_list = []

    def get_context_data(self, **kwargs):
        if self.request.session.get('already_voted'):
            kwargs['already_voted'] = True
            del self.request.session['already_voted']

        self.active_questions_list = []
        self.inactive_questions_list = []

        self.file_contents = read_file()

        for poll in self.file_contents['polls']:
            print ("here ", poll[0][2][0])
            if poll[0][2][0] == 'active':
                self.active_questions_list.append({
                    'question':poll[0][1], 'id':poll[0][0]
                })
            else:
                self.inactive_questions_list.append({
                    'question':poll[0][1], 'id':poll[0][0]
                })

        print ("INactive", self.inactive_questions_list[:])



        '''self.questions_list = []
        self.file_contents = read_file()
        for e in self.file_contents['polls']:
            self.questions_list.append({
                'question':e[0][1], 'id':e[0][0]
            })'''
        #print (self.questions_list)
        kwargs['active_questions'] = self.active_questions_list[:]
        kwargs['inactive_questions'] = self.inactive_questions_list[:]
        return super(PollHome, self).get_context_data(**kwargs)

    def render_to_response(self, context, **response_kwargs):
        votes_made = ""
        response = super(PollHome, self).render_to_response(context, **response_kwargs)
        #print ("previous", type(self.request.COOKIES.get('done_votes')))
        if not self.request.COOKIES.get('done_votes'):
            #print ("None")
            response.set_cookie('done_votes', votes_made, max_age = 365*24*60*60)
        if self.request.session.get('finished_voting'):
            votes_made = self.request.COOKIES.get('done_votes')
            #print ("before append", votes_made)
            votes_made += "*" + self.request.session.get('finished_voting')
            #votes_made.append(self.request.session.get('finished_voting'))
            response.set_cookie('done_votes', votes_made, max_age = 365*24*60*60)
            del self.request.session['finished_voting']
        #print ("After append", self.request.COOKIES.get('done_votes'))
        return response


class PollDetailView(FormView):
    template_name = 'poll_detail.html'
    form_class = BlankForm
    success_url = reverse_lazy('poll:poll_home')
    poll_options = []
    poll_question = None
    poll_options_list = []
    

    def get(self, request, *args, **kwargs):    

        '''voted_questions = self.request.COOKIES.get('done_votes').split('*')
        print ("Voted", voted_questions)'''

        '''if self.kwargs['poll_id'] in voted_questions:
            #messages.add_message(self.request, messages.ERROR, "Vote Already registered for selected Poll !")
            self.request.session['already_voted'] = True    
            return redirect('poll:poll_home')'''

        self.poll_options = []
        self.poll_options_list = []
        question_id = self.kwargs['poll_id']
        #print ("qid " + question_id)
        
        #form = self.form_class()

        file_contents = read_file()
        if not self.request.user.username:
            wallet_obj = Wallet(self.request.COOKIES.get('signed_unblinded_secret')[:6])
            wallet_obj.load_keys()

            #signature = wallet_obj.sign_transaction(self.request.session.get('public_key'), self.kwargs['poll_id'], ans_val)
            bobj = Blockchain(self.request.session['public_key'], 600)
            bobj.load_data()

            if bobj.check_user_poll(self.request.session['public_key'], self.kwargs['poll_id']):
                file_contents = read_file()
                for poll in file_contents['polls']:
                    print ("here 2 ", poll[0][2][0])
                    if poll[0][2][0] == 'active':
                        self.request.session['already_voted'] = True    
                        return redirect('poll:poll_home')

            '''for option in self.poll_options_list:
                if self.poll_options['option_id'] == option:
                    self.poll_options['count'] = bobj.check_vote_count(self.kwargs['poll_id'], option)'''
                
            print ("PO ", self.poll_options)

        else:
            wallet_obj = Wallet(650)
            if not wallet_obj.load_keys():
                wallet_obj.create_keys()
                wallet_obj.save_keys()

            #signature = wallet_obj.sign_transaction(self.request.session.get('public_key'), self.kwargs['poll_id'], ans_val)
            bobj = Blockchain(wallet_obj.public_key, 600)
            bobj.load_data()

        for poll in file_contents['polls']:
            
            if poll[0][0] == int(question_id):
                #print ("if")
                self.poll_question = poll[0][1]
                for option in poll[1:]:
                    self.poll_options_list.append(option[0])
                    self.poll_options.append({
                            'option_id':option[0],
                            'option':option[1],
                            'count': bobj.check_vote_count(self.kwargs['poll_id'], option[0])
                        })

        
        
                

        #print (self.poll_options)

        return super(PollDetailView, self).get(request, *args, **kwargs)
                    
        #print (self.poll_options)
        
        #print (form)
        #print (form.base_fields)
        #print (form.fields)

        #form.base_fields['this'] = form.fields['this'] = forms.CharField(label = 'this')


        


    def get_form(self):
        CHOICES = []
        #print ("GF")
        form = BlankForm()

        #print (form)

        '''for option in self.poll_options:
            #print (option)
            name = 'option_{}'.format(option['option_id'])
            #print (name)
            form.base_fields[name] = form.fields[name] = forms.ChoiceField(initial = option['option'], widget = forms.RadioSelect())'''

        for option in self.poll_options:
            temp = (option['option'], option['option'])
            CHOICES.append(temp)
        
        CHOICES = tuple(CHOICES)
        #print (CHOICES)
        #initial = option['option'], 
        form.base_fields['options'] = form.fields['options'] = forms.ChoiceField(choices = CHOICES, widget = forms.RadioSelect())

        #print (form)
        return form

    def get_context_data(self, **kwargs):
        kwargs['question'] = self.poll_question
        #print ('in kwargs ', self.poll_options)
        kwargs['poll_options'] = self.poll_options
        kwargs['poll_id'] = self.kwargs['poll_id']
        kwargs['inactive'] = False

        file_contents = read_file()

        for poll in file_contents['polls']:

            print ("context ", poll[0][2][0])
            if int(self.kwargs['poll_id']) == poll[0][0]:
                if poll[0][2][0] == 'inactive':
                    kwargs['inactive'] = True
        return super(PollDetailView, self).get_context_data(**kwargs)


    def post(self, request, *args, **kwargs):

        val = self.request.POST.get('options')
        print (val)


        file_contents = read_file()

        for poll in file_contents['polls']:
            
            if poll[0][0] == int(self.kwargs['poll_id']):
                #print ("if")
                self.poll_question = poll[0][1]
                for option in poll[1:]:
                    self.poll_options.append({
                            'option_id':option[0],
                            'option':option[1]
                        })

        print (self.poll_options)
        for option in self.poll_options:
            if option['option'] == val:
                ans_val = option['option_id']

        


        self.request.session['finished_voting'] = self.kwargs['poll_id']

        messages.add_message(self.request, messages.SUCCESS, "Your Vote was Registered Successfully.")
        if not self.request.user.username:
            wallet_obj = Wallet(self.request.COOKIES.get('signed_unblinded_secret')[:6])
            wallet_obj.load_keys()

            #signature = wallet_obj.sign_transaction(self.request.session.get('public_key'), self.kwargs['poll_id'], ans_val)
            bobj = Blockchain(self.request.session['public_key'], 600)
            bobj.load_data()
            signature = wallet_obj.sign_transaction(self.request.session.get('public_key'), self.kwargs['poll_id'], ans_val)
            bobj = Blockchain(self.request.session['public_key'], 600)
            bobj.load_data()
            bobj.add_transaction(self.request.session['public_key'], self.kwargs['poll_id'], signature, ans_val)
        else:
            wallet_obj = Wallet(650)
            if not wallet_obj.load_keys():
                wallet_obj.create_keys()
                wallet_obj.save_keys()

            
        
            #print (option)
        #print (dir(form))
        #print (form)



        '''if form.is_valid:
            print (form.cleaned_data)'''


        return redirect('poll:poll_home')


class EndPoll(TemplateView):
    template_name = 'base.html'

    def get(self, request, *args, **kwargs):
        file_contents = read_file()
        for poll in file_contents['polls']:
            #print ("Poll", poll, type(poll[0][2]))
            #print (poll[0][2][0])
            if int(self.kwargs['poll_id']) == poll[0][0]:
                poll[0][2][0] = 'inactive'
                print ("After", poll)
                write_file(file_contents)
                messages.add_message(self.request, messages.SUCCESS, "Voting Closed Successfully!")
                return redirect('poll:poll_detail', self.kwargs['poll_id'])
        return super(EndPoll, self).get(request, *args, **kwargs)


class MineBlock(View):
    def get(self, request, *args, **kwargs):
        bobj = Blockchain(self.request.session['public_key'], 600)
        bobj.load_data()
        bobj.mine_block()
        print("Printing bobj")
        print(bobj)

        return HttpResponse("Mining successful")


    

