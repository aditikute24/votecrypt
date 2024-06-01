from django import forms

class BlindToValidate(forms.Form):
    secret_id = forms.CharField(label = 'SecretID', widget = forms.TextInput(attrs = {'required':'required', 'class':'form-control form-control-lg'}))
    secret_number = forms.CharField(label = 'Secret Number', widget = forms.TextInput(attrs = {'required':'required', 'class':'form-control form-control-lg'}))

    class Meta:
        fields = '__all__'

class SignedUnblindForm(forms.Form):
    secret_number = forms.CharField(label = 'Secret Number', widget = forms.TextInput(attrs = {'required':'required', 'class':'form-control form-control-lg'}))

    class Meta:
        fields = '__all__'

class VerifyLogin(forms.Form):
    secret_id = forms.CharField(label = 'SecretID', widget = forms.TextInput(attrs = {'required':'required', 'class':'form-control form-control-lg'}))

    class Meta:
        fields = '__all__'

class BlockchainForm(forms.Form):
    blockchain_field = forms.CharField(label = "Blockchain", widget = forms.Textarea(attrs = {'class':'form-control form-control-lg'}))

    class Meta:
        fields = '__all__'


