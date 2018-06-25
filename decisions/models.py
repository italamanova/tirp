from django.db import models


class Alternative(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Alternative name'
    )

    def __str__(self):
        return '%s' % self.name


class LPR(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='LPR name'
    )
    rank = models.IntegerField(
        verbose_name='LPR rank',
        null=True,
        blank=True
    )
    results = models.ManyToManyField(
        Alternative,
        through='Result',
        verbose_name="Results"
    )

    class Meta:
        verbose_name = "LPR"
        verbose_name_plural = "LPR"
        ordering = [
            'rank',
            'name'
        ]

    def __str__(self):
        return '%s' % self.name


class Result(models.Model):
    lpr = models.ForeignKey(
        LPR,
        on_delete=models.CASCADE,
        verbose_name="LPR"
    )
    alternative = models.ForeignKey(
        Alternative,
        on_delete=models.CASCADE,
        verbose_name="Alternative"
    )
    rank = models.IntegerField(
        verbose_name='Result rank',
        null=True,
        blank=True
    )
    alternative_weight = models.IntegerField(
        verbose_name='Alternative weight'
    )

    class Meta:
        verbose_name = "Result"
        verbose_name_plural = "Results"
        ordering = [
            'rank',
            'alternative_weight'
        ]

    def __str__(self):
        return '%s' % self.alternative


class Criteria(models.Model):
    QUALITATIVE = 'ql'
    QUANTITATIVE = 'qn'
    CRITERIA_CHOICE = (
        (QUALITATIVE, 'Qualitative'),
        (QUANTITATIVE, 'Quantitative'),
    )

    MINIMUM = 'min'
    MAXIMUM = 'max'
    OPTIMAl_CHOICE = (
        (MINIMUM, 'Minimum'),
        (MAXIMUM, 'Maximum'),
    )

    name = models.CharField(
        max_length=255,
        verbose_name='Criteria name'
    )
    rank = models.IntegerField(
        verbose_name='Criteria rank',
        null=True,
        blank=True
    )
    weight = models.IntegerField(
        verbose_name='Criteria weight'
    )
    criteria_type = models.CharField(
        max_length=2,
        choices=CRITERIA_CHOICE,
        verbose_name='Criteria type'
    )
    optimal_type = models.CharField(
        max_length=3,
        choices=OPTIMAl_CHOICE,
        verbose_name='Optimal criteria type',
        null=True,
        blank=True
    )
    measure = models.CharField(
        max_length=255,
        verbose_name='Criteria measure'
    )
    scale_type = models.CharField(
        max_length=255,
        verbose_name='Criteria scale type'
    )

    class Meta:
        verbose_name = "Criteria"
        verbose_name_plural = "Criterias"
        ordering = [
            'rank',
            'weight',
            'name'
        ]

    def __str__(self):
        return '%s' % self.name


class Mark(models.Model):
    criteria = models.ForeignKey(
        'Criteria',
        on_delete=models.CASCADE,
        verbose_name='Criteria'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Mark name'
    )
    rank = models.IntegerField(
        verbose_name='Mark rank'
    )
    numeric_value = models.IntegerField(
        verbose_name='Mark numeric equivalent'
    )
    normalized_mark = models.IntegerField(
        verbose_name='Normalized mark',
        null=True,
        blank=True
    )
    vectors = models.ManyToManyField(
        Alternative,
        through='Vector',
        verbose_name='Vectors'
    )

    class Meta:
        verbose_name = "Mark"
        verbose_name_plural = "Marks"
        ordering = [
            'rank',
            'name'
        ]

    def __str__(self):
        return '%s , %s %s' % (self.name, self.criteria.measure, self.numeric_value)


class Vector(models.Model):
    alternative = models.ForeignKey(
        'Alternative',
        on_delete=models.CASCADE,
        verbose_name='Alternative'
    )
    mark = models.ForeignKey(
        'Mark',
        on_delete=models.CASCADE,
        verbose_name='Mark'
    )

    def __str__(self):
        return '%s: %s (%s)' % (self.mark.criteria, self.mark, self.mark.normalized_mark)

    def get_mark_criteria(self):
        return self.mark.criteria


class PairCompare(models.Model):
    first_alternative = models.ForeignKey(
        Alternative,
        on_delete=models.CASCADE,
        verbose_name='First alternative',
        related_name='first_alternative'
    )
    second_alternative = models.ForeignKey(
        Alternative,
        on_delete=models.CASCADE,
        verbose_name='Second alternative',
        related_name='second_alternative'
    )
    lpr = models.ForeignKey(
        LPR,
        on_delete=models.CASCADE,
        verbose_name="LPR"
    )
    result = models.CharField(
        max_length=100,
        null=True
    )

    def __str__(self):
        return '%s: %s %s %s' % (self.lpr, self.first_alternative, self.result, self.second_alternative)

    class Meta:
        unique_together = ('first_alternative', 'second_alternative', 'lpr')


class LPRCompare(models.Model):
    master_lpr = models.ForeignKey(
        LPR,
        on_delete=models.CASCADE,
        verbose_name='Master LPR',
        related_name='master_lpr'
    )
    target_lpr = models.ForeignKey(
        LPR,
        on_delete=models.CASCADE,
        verbose_name='Target LPR',
        related_name='target_lpr'
    )
    result = models.IntegerField(
        max_length=2,
        null=True
    )

    def __str__(self):
        return '%s: %s (%s)' % (self.master_lpr, self.target_lpr, self.result)
