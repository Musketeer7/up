from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


class Message(models.Model):
    STATE_CHOICES = (
        ('P', _('Pending')),
        ('F', _('Failed')),
        ('S', _('Sent')),
        ('D', _('Delivered')),
    )
    text = models.TextField(verbose_name=_('Text'))
    to = models.CharField(max_length=16, verbose_name=_('To'))
    state = models.CharField(max_length=1, default='S', choices=STATE_CHOICES, db_index=True, verbose_name=_('State'))
    reference_code = models.CharField(null=True, max_length=20, verbose_name=_('Reference Code'))
    error = models.CharField(null=True, default='', max_length=50, verbose_name=_('Error'))
    job_type = models.CharField(null=True, max_length=80, verbose_name=_('Job Type'))
    created = models.DateTimeField(default=timezone.now, verbose_name=_('Created Time'))
    backend = models.CharField(max_length=8, verbose_name=_('Backend'))
    description = models.CharField(blank=True, default='', max_length=200, verbose_name=_('Description'))

    def __str__(self):
        summary = (self.text[:17] + '...') if len(self.text) > 20 else self.text
        return 'sms sent to %s (%s)' % (self.to, summary)

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')