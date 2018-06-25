from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from django_filters.views import FilterView

from decisions.models import Mark, Alternative, Vector, Result
from decisions.views import AlternativeListView, AlternativeCreateView, AlternativeDeleteView, AlternativeUpdateView, \
    alt_compare
from decisions.views import CriteriaListView, CriteriaCreateView, CriteriaDeleteView, CriteriaUpdateView
from decisions.views import LPRListView, LPRDetailView, LPRCreateView, LPRDeleteView, LPRUpdateView
from decisions.views import MarkListView, MarkDetailView, MarkCreateView, MarkDeleteView, MarkUpdateView
from decisions.views import VectorListView, VectorDetailView, VectorCreateView, VectorDeleteView, VectorUpdateView, create_vectors, list_vectors
from decisions.views import ResultListView, ResultDetailView, ResultCreateView, ResultDeleteView, ResultUpdateView
from decisions.views import RankCriteriaView, select_alternative_to_compare, compare_alternatives, get_result_matrix, get_group_results, compare_lprs, get_lpr_results

urlpatterns = [
    url(
        r'^alternatives/$',
        login_required(AlternativeListView.as_view()),
        name="alternative-list"
    ),
    url(
        r'^alternatives/create/$',
        login_required(AlternativeCreateView.as_view()),
        name="alternative-create"
    ),
    url(
        r'^alternatives/(?P<pk_alternative>[^/]+)/update/$',
        login_required(AlternativeUpdateView.as_view()),
        name="alternative-update"
    ),
    url(
        r'^alternatives/(?P<pk_alternative>[^/]+)/delete/$',
        login_required(AlternativeDeleteView.as_view()),
        name="alternative-delete"
    ),




    url(
        r'^lprs/$',
        login_required(LPRListView.as_view()),
        name="lpr-list"
    ),
    url(
        r'^lprs/(?P<pk_lpr>[^/]+)/details/$',
        login_required(LPRDetailView.as_view()),
        name="lpr-detail"
    ),
    url(
        r'^lprs/create/$',
        login_required(LPRCreateView.as_view()),
        name="lpr-create"
    ),
    url(
        r'^lprs/(?P<pk_lpr>[^/]+)/update/$',
        login_required(LPRUpdateView.as_view()),
        name="lpr-update"
    ),
    url(
        r'^lprs/(?P<pk_lpr>[^/]+)/delete/$',
        login_required(LPRDeleteView.as_view()),
        name="lpr-delete"
    ),



    # VectorListView.as_view()
    url(
        r'^vectors/$',
        login_required(FilterView.as_view(model=Vector, filter_fields=('alternative', 'mark__criteria',))),
        name="vector-list"
    ),
    url(
        r'^vectors/(?P<pk_vector>[^/]+)/details/$',
        login_required(list_vectors),
        name="vector-detail"
    ),
    url(
        r'^vectors/create/$',
        login_required(create_vectors),
        name="vector-create"
    ),
    url(
        r'^alternative/(?P<pk_alternative>[^/]+)/update-vectors/$',
        login_required(VectorUpdateView.as_view()),
        name="vector-update"
    ),
    url(
        r'^vectors/(?P<pk_vector>[^/]+)/delete/$',
        login_required(VectorDeleteView.as_view()),
        name="vector-delete"
    ),




    url(
        r'^marks/$',
        login_required(FilterView.as_view(model=Mark, filter_fields=('criteria',))),
        name="mark-list"
    ),
    url(
        r'^marks/(?P<pk_mark>[^/]+)/details/$',
        login_required(MarkDetailView.as_view()),
        name="mark-detail"
    ),
    url(
        r'^marks/create/$',
        login_required(MarkCreateView.as_view()),
        name="mark-create"
    ),
    url(
        r'^marks/(?P<pk_mark>[^/]+)/update/$',
        login_required(MarkUpdateView.as_view()),
        name="mark-update"
    ),
    url(
        r'^marks/(?P<pk_mark>[^/]+)/delete/$',
        login_required(MarkDeleteView.as_view()),
        name="mark-delete"
    ),




    url(
        r'^criterias/$',
        login_required(CriteriaListView.as_view()),
        name="criteria-list"
    ),
    url(
        r'^criterias/create/$',
        login_required(CriteriaCreateView.as_view()),
        name="criteria-create"
    ),
    url(
        r'^criterias/(?P<pk_criteria>[^/]+)/update/$',
        login_required(CriteriaUpdateView.as_view()),
        name="criteria-update"
    ),
    url(
        r'^criterias/(?P<pk_criteria>[^/]+)/delete/$',
        login_required(CriteriaDeleteView.as_view()),
        name="criteria-delete"
    ),



    # ResultListView.as_view()
    url(
        r'^results/$',
        login_required(FilterView.as_view(model=Result, filter_fields=('lpr', 'alternative'))),
        name="result-list"
    ),
    url(
        r'^results/(?P<pk_result>[^/]+)/details/$',
        login_required(ResultDetailView.as_view()),
        name="result-detail"
    ),
    url(
        r'^results/create/$',
        login_required(ResultCreateView.as_view()),
        name="result-create"
    ),
    url(
        r'^results/(?P<pk_result>[^/]+)/update/$',
        login_required(ResultUpdateView.as_view()),
        name="result-update"
    ),
    url(
        r'^results/(?P<pk_result>[^/]+)/delete/$',
        login_required(ResultDeleteView.as_view()),
        name="result-delete"
    ),




    # comparing criterias
    url(
        r'^lprs/(?P<pk_lpr>[^/]+)/smart/$',
        login_required(select_alternative_to_compare),
        name="start-smart"
    ),
    url(
        r'^lprs/(?P<pk_lpr>[^/]+)/smart-compare/$',
        login_required(compare_alternatives),
        name="compare-smart"
    ),
    url(
        r'^lprs/(?P<pk_lpr>[^/]+)/lpr-compare/$',
        login_required(compare_lprs),
        name="compare-lprs"
    ),
    url(
        r'^lprs/(?P<pk_lpr>[^/]+)/results/$',
        login_required(get_result_matrix),
        name="get-results"
    ),

    url(
        r'^lprs/(?P<pk_lpr>[^/]+)/incidence/$',
        login_required(alt_compare),
        name="start-incidence"
    ),




    # group results
    url(
        r'^group_results/$',
        login_required(get_group_results),
        name="group-results"
    ),
    url(
        r'^lpr_results/$',
        login_required(get_lpr_results),
        name="lpr-results"
    ),
]