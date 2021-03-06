"""Models used by django-subscribers."""

import hashlib

from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models


def has_int_pk(model):
    """Tests whether the given model has an integer primary key."""
    return (
        isinstance(model._meta.pk, (models.IntegerField, models.AutoField)) and
        not isinstance(model._meta.pk, models.BigIntegerField)
    )


class MailingList(models.Model):

    """A list of subscribers."""

    date_created = models.DateTimeField(
        auto_now_add = True,
    )
    
    date_modified = models.DateTimeField(
        auto_now = True,
    )
    
    name = models.CharField(
        _('Name'),
        max_length = 200,
    )
    
    def __unicode__(self):
        """Returns the name of the mailing list."""
        return self.name
        
    class Meta:
        ordering = ("name",)
        verbose_name = _('Mailing List')
        verbose_name_plural = _('Mailing Lists')


def format_email(email, name=None):
    """Formats the given email address string."""
    if name:
        return u"{name} <{email}>".format(
            name = name,
            email = email,
        )
    return email
        
        
class SubscriberManager(models.Manager):

    """Manager for the subscriber model."""
    
    def subscribe(self, email, first_name="", last_name="", is_subscribed=True, force_save=True):
        """Signs up the given subscriber."""
        needs_update = False
        email = email.lower()
        # Get the subscriber.
        try:
            subscriber = self.get(email=email)
        except self.model.DoesNotExist:
            needs_update = True
            subscriber = Subscriber(email=email)
        else:
            first_name = first_name or subscriber.first_name
            last_name = last_name or subscriber.last_name
        # Update the params.
        if subscriber.first_name != first_name:
            subscriber.first_name = first_name
            needs_update = True
        if subscriber.last_name != last_name:
            subscriber.last_name = last_name
            needs_update = True
        if is_subscribed is not None and subscriber.is_subscribed != is_subscribed:
            subscriber.is_subscribed = is_subscribed
            needs_update = True
        # Save the model.
        if needs_update or force_save:
            subscriber.save()
        return subscriber


class Subscriber(models.Model):

    """A known email address."""
    
    objects = SubscriberManager()

    date_created = models.DateTimeField(
        auto_now_add = True,
        db_index = True,
    )
    
    date_modified = models.DateTimeField(
        auto_now = True,
    )
    
    email = models.EmailField(
        _('E-Mail'),
        unique = True,
    )
    
    first_name = models.CharField(
        _('First name'),
        max_length = 200,
        blank = True,
    )
    
    last_name = models.CharField(
        _('Last name'),
        max_length = 200,
        blank = True,
    )
    
    is_subscribed = models.BooleanField(
        _("Subscribed"),
        default = True,
    )
    
    mailing_lists = models.ManyToManyField(
        MailingList,
        blank = True,
    )
    
    @property
    def full_name(self):
        """Generates the full name of the subscriber, or an empty string."""
        return u" ".join(
            part for part in (self.first_name, self.last_name)
            if part
        )
    
    def clean(self):
        """Cleans the model fields."""
        super(Subscriber, self).clean()
        # Normalise the email address.
        self.email = self.email.lower()
    
    def __unicode__(self):
        """Returns the email string for this address."""
        return format_email(self.email, self.full_name)
        
    class Meta:
        ordering = ("email",)
        verbose_name = _('Subscriber')
        verbose_name_plural = _('Subscribers')

STATUS_PENDING = 0
STATUS_SENT = 1
STATUS_CANCELLED = 2
STATUS_UNSUBSCRIBED = 3
STATUS_ERROR = 4

STATUS_CHOICES = (
    (STATUS_PENDING, _("Pending")),
    (STATUS_SENT, _("Sent")),
    (STATUS_CANCELLED, _("Cancelled")),
    (STATUS_UNSUBSCRIBED, _("Unsubscribed")),
    (STATUS_ERROR, _("Error")),
)


def get_secure_hash(obj, subscriber):
    """
    Returns a secure hash that can be used to identify the subscriber
    of the email email obj.
    """
    return hashlib.sha1(
        "$".join((
            settings.SECRET_KEY,
            unicode(obj.pk).encode("utf-8"),
            str(subscriber.pk),
            str(subscriber.date_created.strftime("%Y-%m-%d-%H-%M-%S")),
        ))
    ).hexdigest()


class DispatchedEmail(models.Model):

    """A batch mailing task."""

    date_created = models.DateTimeField(
        auto_now_add = True,
    )
    
    date_to_send = models.DateTimeField(
        db_index = True,
    )
    
    date_sent = models.DateTimeField(
        db_index = True,
        blank = True,
        null = True,
    )
    
    manager_slug = models.CharField(
        db_index = True,
        max_length = 200,
    )
    
    content_type = models.ForeignKey(
        ContentType,
    )
    
    object_id = models.TextField()
    
    object_id_int = models.IntegerField(
        db_index = True,
        blank = True,
        null = True,
    )
    
    object = generic.GenericForeignKey()
    
    subscriber = models.ForeignKey(
        Subscriber,
    )
    
    status = models.IntegerField(
        default = STATUS_PENDING,
        choices = STATUS_CHOICES,
        db_index = True,
    )
    
    status_message = models.TextField(
        blank = True,
    )
    
    def __unicode__(self):
        """Returns a unicode representation."""
        return unicode(self.object)
        
    class Meta:
        ordering = ("id",)