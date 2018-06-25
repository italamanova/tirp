import itertools
from collections import defaultdict
from operator import attrgetter

from django.core.checks import messages
from django.db import DatabaseError
from django.db.models import F
from django.db.models import Max, Min
from django.forms import formset_factory
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, CreateView, DeleteView, View
from django.views.generic.list import ListView

from decisions.filters import VectorFilter
from decisions.forms import CreateVectorForm, UpdateVectorForm, LPRCriteriasForm, AlternativeSelectionForm, \
    LPRCompareForm, AltCompareForm
from decisions.models import Alternative, LPR, Result, Criteria, Mark, Vector, PairCompare, LPRCompare

import networkx as nx


################
# Alternatives #
################


class AlternativeListView(ListView):
    model = Alternative


class AlternativeUpdateView(UpdateView):
    model = Alternative
    pk_url_kwarg = 'pk_alternative'

    fields = [
        'name',
    ]

    template_name_suffix = '_update'

    def get_success_url(self):
        return reverse_lazy('alternative-list')


class AlternativeDeleteView(DeleteView):
    model = Alternative
    pk_url_kwarg = 'pk_alternative'

    def get_success_url(self):
        return reverse_lazy('alternative-list')


class AlternativeCreateView(CreateView):
    model = Alternative
    pk_url_kwarg = 'pk_alternative'

    fields = [
        'name',
    ]

    template_name_suffix = '_create'

    def form_valid(self, form):
        response = super(AlternativeCreateView, self).form_valid(form)
        for lpr in LPR.objects.all():
            PairCompare.objects.create(first_alternative=self.object, second_alternative=self.object, result="=",
                                       lpr=lpr)
        return response

    def get_success_url(self):
        return reverse_lazy('alternative-list')

    #############
    # Criterias #
    #############


class CriteriaListView(ListView):
    model = Criteria


class CriteriaUpdateView(UpdateView):
    model = Criteria
    pk_url_kwarg = 'pk_criteria'

    fields = [
        'name',
        'rank',
        'weight',
        'criteria_type',
        'optimal_type',
        'measure',
        'scale_type',
    ]

    template_name_suffix = '_update'

    def form_valid(self, form):
        response = super(CriteriaUpdateView, self).form_valid(form)
        if self.object.optimal_type == "max":
            top = Mark.objects.filter(criteria=self.object).aggregate(Max('numeric_value'))
            top = top["numeric_value__max"]
            Mark.objects.filter(criteria=self.object).update(normalized_mark=(F("numeric_value") * 100 / top))
        elif self.object.optimal_type == "min":
            top = Mark.objects.filter(criteria=self.object).aggregate(Min('numeric_value'))
            top = top["numeric_value__min"]
            Mark.objects.filter(criteria=self.object).update(normalized_mark=(top * 100 / F("numeric_value")))
        return response

    def get_success_url(self):
        return reverse_lazy('criteria-list')


class CriteriaDeleteView(DeleteView):
    model = Criteria
    pk_url_kwarg = 'pk_criteria'

    def get_success_url(self):
        return reverse_lazy('criteria-list')


class CriteriaCreateView(CreateView):
    model = Criteria
    pk_url_kwarg = 'pk_criteria'

    fields = [
        'name',
        'rank',
        'weight',
        'criteria_type',
        'optimal_type',
        'measure',
        'scale_type',
    ]

    template_name_suffix = '_create'

    def get_success_url(self):
        return reverse_lazy('criteria-list')

    ########
    # LPRs #
    ########


class LPRListView(ListView):
    model = LPR


class LPRDetailView(DetailView):
    model = LPR
    pk_url_kwarg = 'pk_lpr'


class LPRUpdateView(UpdateView):
    model = LPR
    pk_url_kwarg = 'pk_lpr'

    fields = [
        'name',
        'rank',
        # 'results',
    ]

    template_name_suffix = '_update'

    def get_success_url(self):
        return reverse_lazy('lpr-list')


class LPRDeleteView(DeleteView):
    model = LPR
    pk_url_kwarg = 'pk_lpr'

    def get_success_url(self):
        return reverse_lazy('lpr-list')


class LPRCreateView(CreateView):
    model = LPR
    pk_url_kwarg = 'pk_lpr'

    fields = [
        'name',
        'rank',
        # 'results',
    ]

    template_name_suffix = '_create'

    def form_valid(self, form):
        response = super(LPRCreateView, self).form_valid(form)
        LPRCompare.objects.create(master_lpr=self.object, target_lpr=self.object, result=1)
        return response

    def get_success_url(self):
        return reverse_lazy('lpr-list')

    #########
    # Marks #
    #########


class MarkListView(ListView):
    model = Mark


class MarkDetailView(DetailView):
    model = Mark
    pk_url_kwarg = 'pk_mark'


class MarkUpdateView(UpdateView):
    model = Mark
    pk_url_kwarg = 'pk_mark'

    fields = [
        'criteria',
        'name',
        'rank',
        'numeric_value',
        'normalized_mark',
        # 'vectors',
    ]

    template_name_suffix = '_update'

    def form_valid(self, form):
        response = super(MarkUpdateView, self).form_valid(form)
        if self.object.criteria.optimal_type == "max":
            top = Mark.objects.filter(criteria=self.object.criteria).aggregate(Max('numeric_value'))
            top = top["numeric_value__max"]
            Mark.objects.filter(criteria=self.object.criteria).update(normalized_mark=(F("numeric_value") * 100 / top))
        elif self.object.criteria.optimal_type == "min":
            top = Mark.objects.filter(criteria=self.object.criteria).aggregate(Min('numeric_value'))
            top = top["numeric_value__min"]
            Mark.objects.filter(criteria=self.object.criteria).update(normalized_mark=(top * 100 / F("numeric_value")))
        return response

    def get_success_url(self):
        return reverse_lazy('mark-list')


class MarkDeleteView(DeleteView):
    model = Mark
    pk_url_kwarg = 'pk_mark'

    def get_success_url(self):
        return reverse_lazy('mark-list')


class MarkCreateView(CreateView):
    model = Mark
    pk_url_kwarg = 'pk_mark'

    fields = [
        'criteria',
        'name',
        'rank',
        'numeric_value',
        'normalized_mark',
        # 'vectors',
    ]

    template_name_suffix = '_create'

    def form_valid(self, form):
        response = super(MarkCreateView, self).form_valid(form)
        if self.object.criteria.optimal_type == "max":
            top = Mark.objects.filter(criteria=self.object.criteria).aggregate(Max('numeric_value'))
            top = top["numeric_value__max"]
            Mark.objects.filter(criteria=self.object.criteria).update(normalized_mark=(F("numeric_value") * 100 / top))
        elif self.object.criteria.optimal_type == "min":
            top = Mark.objects.filter(criteria=self.object.criteria).aggregate(Min('numeric_value'))
            top = top["numeric_value__min"]
            Mark.objects.filter(criteria=self.object.criteria).update(normalized_mark=(top * 100 / F("numeric_value")))
        return response

    def get_success_url(self):
        return reverse_lazy('mark-list')

    ###########
    # Vectors #
    ###########


class VectorListView(ListView):
    model = Vector
    template_name = 'vectors/decisions/vector_list.html'


def list_vectors(request):
    filter_obj = VectorFilter(request.GET, queryset=Vector.objects.select_related.all())
    print(filter_obj)
    return render(request, 'vectors/decisions/vector_filter.html', {'filter': filter_obj})


class VectorDetailView(DetailView):
    model = Vector
    pk_url_kwarg = 'pk_vector'


class VectorUpdateView(UpdateView):
    pk_url_kwarg = 'pk_alternative'
    model = Alternative
    form_class = UpdateVectorForm

    template_name = 'vectors/decisions/vector_update.html'

    def get_success_url(self):
        return reverse_lazy('vector-list')


class VectorDeleteView(DeleteView):
    model = Vector
    pk_url_kwarg = 'pk_vector'

    def get_success_url(self):
        return reverse_lazy('vector-list')


"""
def update_vectors(request):
    if request.method == 'POST':
        form = VectorForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = VectorForm()
    return render(request, 'vectors/decisions/vector_create.html', {'form': form})
"""


def create_vectors(request):
    if request.method == 'POST':
        form = CreateVectorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('vector-list'))
    else:
        form = CreateVectorForm()
    return render(request, 'vectors/decisions/vector_create.html', {'form': form})


class VectorCreateView(View):
    form_class = CreateVectorForm

    template_name = 'vectors/decisions/vector_create.html'

    def get_success_url(self):
        return reverse_lazy('vector-list')

    ###########
    # Results #
    ###########


class ResultListView(ListView):
    model = Result


class ResultDetailView(DetailView):
    model = Result
    pk_url_kwarg = 'pk_result'


class ResultUpdateView(UpdateView):
    model = Result
    pk_url_kwarg = 'pk_result'

    fields = [
        'lpr',
        'alternative',
        'rank',
        'alternative_weight',
    ]

    template_name_suffix = '_update'

    def get_success_url(self):
        return reverse_lazy('result-list')


class ResultDeleteView(DeleteView):
    model = Result
    pk_url_kwarg = 'pk_result'

    def get_success_url(self):
        return reverse_lazy('result-list')


class ResultCreateView(CreateView):
    model = Result
    pk_url_kwarg = 'pk_result'

    fields = [
        'lpr',
        'alternative',
        'rank',
        'alternative_weight',
    ]

    template_name_suffix = '_create'

    def get_success_url(self):
        return reverse_lazy('result-list')

    ##########
    # MATRIX #
    ##########

    #########
    # SMART #
    #########


class RankCriteriaView(UpdateView):
    pk_url_kwarg = 'pk_lpr'
    model = LPR
    form_class = LPRCriteriasForm

    template_name = 'SMART/decisions/rank_criterias.html'

    def get_success_url(self):
        return reverse_lazy('vector-list')


def select_alternative_to_compare(request, pk_lpr):
    if request.method == 'POST':
        form = AlternativeSelectionForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['first_alternative'] != form.cleaned_data['second_alternative']:
                first_alternative = form.cleaned_data['first_alternative'].id
                second_alternative = form.cleaned_data['second_alternative'].id
                request.session['first_alternative'] = first_alternative
                request.session['second_alternative'] = second_alternative
                return redirect(reverse_lazy('compare-smart', kwargs={'pk_lpr': str(pk_lpr)}))
    else:
        form = AlternativeSelectionForm()
    return render(request, 'SMART/decisions/select_alternatives.html', {
        'form': form,
        "lpr": LPR.objects.get(id=pk_lpr)
    })


def compare_alternatives(request, pk_lpr):
    first_plus = []
    first_minus = []
    second_plus = []
    second_minus = []
    first_alternative = request.session.get('first_alternative'),
    second_alternative = request.session.get('second_alternative')
    obj_lpr = LPR.objects.get(id=pk_lpr)

    if request.method == 'POST':
        first_object = Alternative.objects.get(id=first_alternative[0])
        second_object = Alternative.objects.get(id=second_alternative)
        # form = AlternativeSelectionForm(request.POST)
        # if form.is_valid():
        print(request.POST)
        if ("Choose " + str(first_object)) in request.POST.get(str(first_object), "-"):
            print("passed")
            PairCompare.objects.update_or_create(first_alternative=first_object, second_alternative=second_object,
                                                 lpr=obj_lpr, defaults={"result": ">"})
            PairCompare.objects.update_or_create(first_alternative=second_object, second_alternative=first_object,
                                                 lpr=obj_lpr, defaults={"result": "<"})
            return redirect(reverse_lazy('lpr-list'))
        elif "Choose " + str(second_object) in request.POST.get(str(second_object), "-"):
            PairCompare.objects.update_or_create(first_alternative=second_object, second_alternative=first_object,
                                                 lpr=obj_lpr, defaults={"result": ">"})
            PairCompare.objects.update_or_create(first_alternative=first_object, second_alternative=second_object,
                                                 lpr=obj_lpr, defaults={"result": "<"})
            return redirect(reverse_lazy('lpr-list'))
        elif "Choose both" in request.POST.get("Choose both", "-"):
            PairCompare.objects.update_or_create(first_alternative=second_object, second_alternative=first_object,
                                                 lpr=obj_lpr, defaults={"result": "="})
            PairCompare.objects.update_or_create(first_alternative=first_object, second_alternative=second_object,
                                                 lpr=obj_lpr, defaults={"result": "="})
            return redirect(reverse_lazy('lpr-list'))
    else:
        first_set = Alternative.objects.get(id=first_alternative[0]).vector_set.all()
        second_set = Alternative.objects.get(id=second_alternative).vector_set.all()
        if len(first_set) == len(second_set):
            for i in range(len(first_set)):
                if first_set[i].mark.criteria.optimal_type == "max":
                    if int(first_set[i].mark.numeric_value) > int(second_set[i].mark.numeric_value):
                        first_plus.append(first_set[i])
                        second_minus.append(second_set[i])
                    elif int(first_set[i].mark.numeric_value) < int(second_set[i].mark.numeric_value):
                        first_minus.append(first_set[i])
                        second_plus.append(second_set[i])
                elif first_set[i].mark.criteria.optimal_type == "min":
                    if int(first_set[i].mark.numeric_value) < int(second_set[i].mark.numeric_value):
                        first_plus.append(first_set[i])
                        second_minus.append(second_set[i])
                    elif int(first_set[i].mark.numeric_value) > int(second_set[i].mark.numeric_value):
                        first_minus.append(first_set[i])
                        second_plus.append(second_set[i])

    return render(request, 'SMART/decisions/compare_alternatives.html', {
        'first_alternative': Alternative.objects.get(id=first_alternative[0]),
        'second_alternative': Alternative.objects.get(id=second_alternative),
        'first_plus': sorted(first_plus, key=attrgetter('mark.normalized_mark'), reverse=True),
        'first_minus': sorted(first_minus, key=attrgetter('mark.normalized_mark'), reverse=True),
        'second_plus': sorted(second_plus, key=attrgetter('mark.normalized_mark'), reverse=True),
        'second_minus': sorted(second_minus, key=attrgetter('mark.normalized_mark'), reverse=True),
        "lpr": LPR.objects.get(id=pk_lpr)
    })


def get_result_matrix(request, pk_lpr):
    pair_compares = PairCompare.objects.filter(lpr=LPR.objects.get(id=pk_lpr))
    alternatives = Alternative.objects.all()
    results = []
    count_sign = []
    max_alternatives = []
    listed_alts = []
    max_sign = 0
    if request.method == "GET":
        results = []
        i = 0
        for a_alternative in alternatives:
            results.append([])
            for s_alternative in alternatives:
                try:
                    print(pair_compares.get(
                        first_alternative=a_alternative,
                        second_alternative=s_alternative
                    ))
                    results[i].append(pair_compares.get(
                        first_alternative=a_alternative,
                        second_alternative=s_alternative
                    ))
                except PairCompare.DoesNotExist:
                    results[i].append("")

            i = i + 1
        for t in range(len(alternatives)):
            list_len = 0
            for n in range(len(results[t])):
                if results[t][n] != "" and results[t][n].result in [">", ">=", "="]:
                    list_len = list_len + 1
            if list_len > max_sign:
                max_alternatives.clear()
                max_alternatives.append(alternatives[t])
                max_sign = list_len
            elif list_len == max_sign:
                max_alternatives.append(alternatives[t])

        print(max_alternatives)

        listed_alts = dict(zip(alternatives, results))

    return render(request, 'SMART/decisions/results.html', {
        "max_alternatives": max_alternatives,
        "alternatives": alternatives,
        "listed_alts": listed_alts,
        "lpr": LPR.objects.get(id=pk_lpr)
    })


def get_group_results(request):
    if request.method == "GET":
        standard_keys = range(1, len(Alternative.objects.all()) + 1)
        results = {}
        alt_results = defaultdict(int)
        t_results = {}
        lpr_list = LPR.objects.all()
        i = 0
        for lpr in LPR.objects.all():
            results[lpr] = defaultdict(list)
            results[lpr] = {key: [] for key in standard_keys}
            for alternative in Alternative.objects.all():
                pairs = len(PairCompare.objects.filter(
                    first_alternative=alternative,
                    lpr=lpr,
                    result__in=[">", ">=", "="]
                ))
                Result.objects.update_or_create(
                    lpr=lpr,
                    alternative=alternative,
                    rank=1,
                    defaults={
                        'alternative_weight': pairs
                    }
                )
                results[lpr][pairs].append(str(alternative))
                lpr_rank = lpr.rank if lpr.rank is not None else 0
                alt_results[alternative] += pairs * lpr_rank

        for i in range(1, len(Alternative.objects.all()) + 1):
            t_results[i] = {}
            for lpr in lpr_list:
                t_results[i][lpr] = list(Result.objects.filter(alternative_weight=i, lpr=lpr))

        for i in range(1, len(t_results) + 1):
            print(t_results[i])

        return render(request, 'SMART/decisions/group_results.html', {
            "results": results,
            "alt_results": dict(alt_results),
            "t_results": t_results,
            "lprs": lpr_list
        })


def compare_lprs(request, pk_lpr):
    obj_lpr = LPR.objects.get(id=pk_lpr)
    lprs = None
    print(obj_lpr)
    if request.method == 'POST':
        form = LPRCompareForm(request.POST, pk_lpr=pk_lpr)
        print("sff")
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('lpr-list'))
    else:
        form = LPRCompareForm(pk_lpr=pk_lpr)
    return render(request, 'lprs/decisions/lpr_compare.html', {'form': form})


def get_lpr_results(request):
    lprs = LPR.objects.all()
    lpr_lists = {}
    lpr_results = {}
    nor_lists = {}
    plus_results = {}
    t_results = {}
    nor_results = {}
    i = 0
    for lpr in lprs:
        lpr_results[lpr] = 0
        plus_results[lpr] = 0
        nor_results[lpr] = 0
        t_results[lpr] = 0
        nor_lists[lpr] = []
    if request.method == "GET":
        for lpr_1 in lprs:
            lpr_lists[lpr_1] = []
            for lpr_2 in lprs:
                try:
                    lpr_lists[lpr_1].append(LPRCompare.objects.get(master_lpr=lpr_2, target_lpr=lpr_1))
                    lpr_results[lpr_1] += LPRCompare.objects.get(master_lpr=lpr_2, target_lpr=lpr_1).result
                    nor_lists[lpr_1].append(LPRCompare.objects.get(master_lpr=lpr_2, target_lpr=lpr_1).result)
                except Exception as e:
                    lpr_lists[lpr_1].append("")
                    nor_lists[lpr_1].append(0)

            i += 1

    for lpr in lprs:
        t_results[lpr] = lpr_results[lpr]

    for i in range(5):
        for lpr_1 in lprs:
            for lpr_2 in lprs:
                try:
                    plus_results[lpr_1] += t_results[lpr_2] * LPRCompare.objects.get(master_lpr=lpr_2,
                                                                                     target_lpr=lpr_1).result
                except Exception as e:
                    plus_results[lpr_1] += 0

        if i < 4:

            for lpr in lprs:
                t_results[lpr] = plus_results[lpr]
                plus_results[lpr] = 0

    nor_sum = sum(plus_results.values())
    for t, k in plus_results.items():
        nor_results[t] = int((k / nor_sum) * 100)

    for lpr in lprs:
        LPR.objects.filter(id=lpr.id).update(rank=nor_results[lpr])

    return render(request, 'lprs/decisions/lpr_results.html', {
        "nor_results": nor_results,
        "plus_results": plus_results,
        "lpr_lists": lpr_lists,
        "lpr_results": lpr_results,
        "lprs": lprs
    })


def alt_compare(request, pk_lpr):
    obj_lpr = LPR.objects.get(id=pk_lpr)
    pair_compares = PairCompare.objects.filter(lpr=LPR.objects.get(id=pk_lpr))
    alternatives = Alternative.objects.all()

    compare_list = []
    for first_alternative, second_alternative in itertools.combinations(alternatives, 2):
        compare_list.append({'first': first_alternative, 'second': second_alternative})

    CompareFormSet = formset_factory(AltCompareForm)

    formset_initial = []
    for item in compare_list:
        pair_initial = {'first_alternative': item['first'],
                        'second_alternative': item['second']
                        }
        try:
            pair = pair_compares.get(
                first_alternative=item['first'],
                second_alternative=item['second']
            )
        except PairCompare.DoesNotExist:
            pair = None

        if pair:
            pair_initial['compare'] = pair.result
        formset_initial.append(pair_initial)

    _formset = CompareFormSet(initial=formset_initial, prefix='compare')

    if request.method == "POST":
        new_formset = CompareFormSet(request.POST, initial=formset_initial, prefix='compare')
        if new_formset.is_valid():
            for form in new_formset:
                if form.is_valid():
                    if form.cleaned_data.get('compare'):
                        pair_object, created = PairCompare.objects.get_or_create(
                            first_alternative=form.first_alternative,
                            second_alternative=form.second_alternative,
                            lpr=obj_lpr)
                        pair_object.result = form.cleaned_data['compare']
                        pair_object.save()

            return redirect('lpr-list')

    return render(request, 'incidence/decisions/alt_compare.html', {
        'formset': _formset,
        "alternatives": alternatives,
        "lpr": LPR.objects.get(id=pk_lpr)
    })


def create_incidence_matrix(request, pk_lpr):
    obj_lpr = LPR.objects.get(id=pk_lpr)
    pair_compares = PairCompare.objects.filter(lpr=LPR.objects.get(id=pk_lpr))
    alternatives = Alternative.objects.all()
    len_alternatives = len(alternatives)

    nodes_dict = {}
    nodes = []
    edges = []
    result = []

    for i in range(0, len_alternatives):
        nodes.append(i)
        nodes_dict[alternatives[i].name] = i

    inv_nodes_dict = {v: k for k, v in nodes_dict.items()}

    print(nodes_dict)

    for pair in pair_compares:
        node1 = nodes_dict[pair.first_alternative.name]
        node2 = nodes_dict[pair.second_alternative.name]
        if pair.result == '>':
            edges.append([node1, node2])
        if pair.result == '<':
            edges.append([node2, node1])
        if pair.result == '=':
            edges.append([node1, node2])
            edges.append([node2, node1])

    print(edges)

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    incidence_matrix = -nx.incidence_matrix(G, oriented=True)  # this returns a scipy sparse matrix

    array_incidence_matrix = incidence_matrix.toarray()

    for number in range(0, len(array_incidence_matrix)):
        row = array_incidence_matrix[number]
        if all(i >= 0 for i in row):
            result.append(inv_nodes_dict[number])

    return render(request, 'incidence/decisions/incidence_matrix.html', {
        'incidence_matrix': array_incidence_matrix,
        'nodes_dict': inv_nodes_dict,
        'result': result,
        'lpr': LPR.objects.get(id=pk_lpr)
    })
