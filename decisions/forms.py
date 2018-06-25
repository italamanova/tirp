from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.formsets import BaseFormSet
from django.forms.widgets import PasswordInput, TextInput
from django.utils.translation import ugettext_lazy as _

from decisions.models import Criteria, Mark, Vector, Alternative, LPR, LPRCompare


class CustomAuthForm(AuthenticationForm):
    """
    Custom Form for User Authentication.
    """
    username = forms.CharField(
        widget=TextInput(
            attrs={
                'class': 'validate',
                'placeholder': 'Username'
            }
        )
    )
    password = forms.CharField(
        widget=PasswordInput(
            attrs={
                'placeholder': 'Password'
            }
        )
    )


class CreateVectorForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(CreateVectorForm, self).__init__(*args, **kwargs)
        """
        alternatives = Alternative.objects.all()
        qs = []
        for alt in alternatives:
            if alt.vector_set:
                qs.append(alt)
        """
        alternative = forms.ModelChoiceField(queryset=Alternative.objects.all())
        self.fields['alternative'] = alternative
        criterias = Criteria.objects.all()
        for criteria in criterias:
            field_name = '%s' % criteria
            self.fields[field_name] = forms.ModelChoiceField(queryset=Mark.objects.filter(criteria=criteria))

    def save(self):
        alternative = Alternative.objects.get(name=self.cleaned_data['alternative'])
        alternative.vector_set.all().delete()
        criterias = Criteria.objects.all()
        for criteria in criterias:
            Vector.objects.create(
                alternative=alternative,
                mark=self.cleaned_data[criteria.name],
            )


class UpdateVectorForm(forms.ModelForm):
    disabled_fields = ('name',)

    class Meta:
        model = Alternative
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UpdateVectorForm, self).__init__(*args, **kwargs)
        criterias = Criteria.objects.all()
        for field in self.disabled_fields:
            self.fields[field].disabled = True
        for criteria in criterias:
            field_name = '%s' % criteria
            self.fields[field_name] = forms.ModelChoiceField(queryset=Mark.objects.filter(criteria=criteria))
            print(Vector.objects.get(alternative=self.instance, mark__in=criteria.mark_set.all()).mark)
            self.fields[field_name].initial = Vector.objects.get(alternative=self.instance,
                                                                 mark__in=criteria.mark_set.all()).mark

    def save(self):
        alternative = self.instance
        alternative.name = self.cleaned_data['name']
        alternative.vector_set.all().delete()
        criterias = Criteria.objects.all()
        for criteria in criterias:
            Vector.objects.create(
                alternative=alternative,
                mark=self.cleaned_data[criteria.name],
            )


class LPRCriteriasForm(forms.ModelForm):
    disabled_fields = ('name',)

    class Meta:
        model = LPR
        exclude = ('rank', 'results')

    def __init__(self, *args, **kwargs):
        super(LPRCriteriasForm, self).__init__(*args, **kwargs)
        criterias = Criteria.objects.all()
        for field in self.disabled_fields:
            self.fields[field].disabled = True
        for criteria in criterias:
            field_name = '%s' % criteria
            self.fields[field_name] = forms.IntegerField()
            self.fields[field_name].initial = Criteria.objects.get(name=criteria.name).weight

    def save(self):
        lpr = self.instance
        lpr.name = self.cleaned_data['name']
        criterias = Criteria.objects.all()
        sum_weight = 0
        for criteria in criterias:
            sum_weight += int(self.cleaned_data[criteria.name])
        print(sum_weight)
        for criteria in criterias:
            Criteria.objects.filter(name=criteria.name).update(
                weight=self.cleaned_data[criteria.name]
            )


class AlternativeSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AlternativeSelectionForm, self).__init__(*args, **kwargs)
        first_alternative = forms.ModelChoiceField(queryset=Alternative.objects.all())
        second_alternative = forms.ModelChoiceField(queryset=Alternative.objects.all())
        self.fields['first_alternative'] = first_alternative
        self.fields['second_alternative'] = second_alternative


class AlternativeComparingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.first_alternative = kwargs.pop('first_alternative')
        self.second_alternative = kwargs.pop('second_alternative')

        super(AlternativeComparingForm, self).__init__(*args, **kwargs)
        self.fields['first_alternative'] = self.first_alternative
        self.fields['first_alternative'].widget.attrs['readonly'] = True

        self.fields['second_alternative'] = self.second_alternative
        self.fields['second_alternative'].widget.attrs['readonly'] = True

        first_criterias = Criteria.objects.all()
        for criteria in first_criterias:
            field_name = 'first_%s' % criteria
            self.fields[field_name] = forms.CharField(
                queryset=Vector.objects.get(alternative=self.instance, mark__in=criteria.mark_set.all()).mark
            )
            self.fields[field_name].widget.attrs['readonly'] = True

        second_criterias = Criteria.objects.all()
        for criteria in second_criterias:
            field_name = 'second_%s' % criteria
            self.fields[field_name] = forms.CharField(
                queryset=Vector.objects.get(alternative=self.instance, mark__in=criteria.mark_set.all()).mark
            )
            self.fields[field_name].widget.attrs['readonly'] = True


class LPRCompareForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.pk_lpr = kwargs.pop('pk_lpr')
        super(LPRCompareForm, self).__init__(*args, **kwargs)
        lpr_obj = LPR.objects.get(id=self.pk_lpr)
        self.fields["pk_lpr"] = forms.CharField()
        self.fields["pk_lpr"].disabled = True
        if len(LPRCompare.objects.filter(master_lpr=lpr_obj.id, target_lpr=lpr_obj.id)) == 1:
            self.fields["pk_lpr"].initial = LPR.objects.get(id=lpr_obj.id).name

        for lpr in LPR.objects.exclude(id=lpr_obj.id):
            field_name = '%s' % lpr.name
            self.fields[field_name] = forms.IntegerField()
            if len(LPRCompare.objects.filter(master_lpr=lpr_obj.id, target_lpr=lpr.id)) == 1:
                self.fields[field_name].initial = LPRCompare.objects.get(master_lpr=lpr_obj.id,
                                                                         target_lpr=lpr.id).result

    def save(self):
        print(self.cleaned_data)
        master_lpr = LPR.objects.get(name=self.cleaned_data['pk_lpr'])
        lprs = LPR.objects.exclude(name=self.cleaned_data['pk_lpr'])
        for lpr in lprs:
            LPRCompare.objects.update_or_create(
                master_lpr=master_lpr,
                target_lpr=lpr,
                defaults={
                    "result": self.cleaned_data[lpr.name]
                }
            )


class AltCompareForm(forms.Form):
    COMPARE_CHOICES = (
        ('>', _("Better")),
        ('<', _("Worse")),
        ('=', _("Equal"))
    )

    compare = forms.ChoiceField(choices=COMPARE_CHOICES)

    def __init__(self, *args, **kwargs):
        super(AltCompareForm, self).__init__(*args, **kwargs)

        self.first_alternative = kwargs.get('initial', {}).get('first_alternative', None)
        self.second_alternative = kwargs.get('initial', {}).get('second_alternative', None)

        if self.first_alternative:
            self.first_vector = Alternative.objects.get(id=self.first_alternative.id).vector_set.all()
            self.second_vector = Alternative.objects.get(id=self.second_alternative.id).vector_set.all()
