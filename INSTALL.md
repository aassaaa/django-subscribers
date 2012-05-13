A little later than I expected, here's a rough outline of how to use django-subscrivers.

Firstly, django-subscribers has a few main functions:

User subscription via web form or AJAX.
User unsubscription via secure unguessable URL.
Bulk mailing of newsletters.

To enable the subscription / unsubscription functionality, you need to add the app to your INSTALLED apps setting, and add an entry to your urlpatterns like this:

    url("^", include("subscribers.urls")),

You can then edit the following templates to customise the UI of this workflow. Minimal example templates are provided in the project:

    subscribers/subscribe.html
    subscribers/subscribe_success.html
    subscribers/unsubscribe.html
    subscribers/unsubscribe_success.html

With the subscribe form, you can POST an email, and then optionally the following fields:

    first_name
    last_name
    name

This gives you a fair bit of flexibility in terms of what data you collect from your users.

To enable the bulk mailing functionality, you need to create an app (typically called newsletters), and a model (typically called Newsletter). The model represents the newsletters that will be sent, and minimally would include something like this:

    class Newsletter(models.Model):

        date_created = models.DateTimeField(
            auto_now_add = True,
            db_index = True,
        )

        date_modified = models.DateTimeField(
            auto_now = True,
        )

        subject = models.CharField(
            max_length = 1000,
        )

        content = models.TextField(
            blank = True,
        )

        def __unicode__(self):
            return self.subject

        class Meta:
            ordering = ("-date_created",)

You then register this model with an instance of subscribers.EmailAdmin, customised as necessary to suit your needs. The EmailAdmin class gives you the controls needed to test and send your newsletter.

You then override the following templates to render the content of your newsletter:

    subscribers/email.html
    subscribers/email.txt

There are minimal templates provided in the project. Each template is provided with the following context params when rendering:

    {{subject}} - subject of the email
    {{obj}} - the newsletter model instance being rendered
    {{host}} - the hostname of the site (if sites framework is used or settings.SITE_DOMAIN is set)
    {{view_url}} - the URL on which the email can be viewed online (generated secure personalised url)
    {{unsubscribe_url}} - the URL on which the user can unsubscribe online
    {{subscriber}} - object representing recipient of the email

You then need to set up a cronjob to take care of the background bulk-sending of emails. This cronjob needs to run the ./manage.py sendemailbatch command on a regular (eg. 5 minute) interval. Check out the management command source code for available arguments.

That'll get you started. A whole lot of the functionality is customisable by calling subscribers.register() on your Newsletter model, but I'll leave that as an exercise to you to read through the source code if you need customization beyond what I've outlined above.