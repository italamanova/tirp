from django.contrib import admin

from decisions.models import Alternative, LPR, Result, Criteria, Mark, Vector


class AlternativeAdmin(admin.ModelAdmin):
	list_display = [
		'name'
	]


class LPRAdmin(admin.ModelAdmin):
	list_display = [
		'name',
		'rank',
	]


class ResultAdmin(admin.ModelAdmin):
	list_display = [
		'lpr',
		'alternative',
		'rank',
		'alternative_weight'
	]


class CriteriaAdmin(admin.ModelAdmin):
	list_display = [
		'name',
		'rank',
		'weight',
		'criteria_type',
		'optimal_type',
		'measure',
		'scale_type'
	]


class MarkAdmin(admin.ModelAdmin):
	list_display = [
		'criteria',
		'name',
		'rank',
		'numeric_value',
		'normalized_mark',
	]
	list_filter = ('criteria',)

class VectorAdmin(admin.ModelAdmin):
	list_display = [
		'alternative',
		'get_mark_criteria',
		'mark'
	]
	list_filter = ('alternative',)

	readonly_fields = ('get_mark_criteria',)


admin.site.register(Alternative, AlternativeAdmin)
admin.site.register(LPR, LPRAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Criteria, CriteriaAdmin)
admin.site.register(Mark, MarkAdmin)
admin.site.register(Vector, VectorAdmin)