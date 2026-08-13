Authentication
==============

Who may sign in, and how, is decided by this package rather than by topobank:
ce-ui supplies the user model, registers the django-allauth providers and holds
the settings below. topobank itself is agnostic of the sign-in procedure.

An account is created with an ORCID iD, and no other way
--------------------------------------------------------

An `ORCID <https://orcid.org>`_ iD is what identifies the researcher behind an
account, and what publishing a dataset requires, so it is where an account
begins. Registering with an email address and a password is closed
(``ACCOUNT_ALLOW_SIGNUP``), and a provider that is not listed in
``SOCIALACCOUNT_SIGNUP_PROVIDERS`` cannot create one either: signing in with
Google while holding no account here lands on a page explaining how to get one.

Once an account exists, further ways of reaching it can be attached to it from
the *Connected identities* page (``/accounts/3rdparty/``):

- another identity provider, currently Google,
- a password, set from the profile,
- further email addresses, any of which can then be used to sign in.

Connecting a provider also records any address it has already verified, so a
Google account brings its address with it and no confirmation mail is needed.
django-allauth does this when a provider *creates* an account but leaves it
undone when one is connected, so ``ce_ui.users.signals`` fills the gap. An
address is skipped if any account already holds it — addresses are unique
(``ACCOUNT_UNIQUE_EMAIL``), and taking one would hand over its sign-in.

The ORCID account itself cannot be disconnected — it is what the account *is*.
Everything else can be removed again, as long as one way of signing back in
remains.

How Google finds the right account
..................................

Because Google cannot create an account, a Google sign-in has to find one that
already exists. It is matched by email address: if a confirmed address on some
account equals the address Google reports — and Google has verified that
address itself — the sign-in lands on that account, and the Google account is
connected to it so that later sign-ins are recognised directly. Otherwise the
sign-in is refused.

Two conditions, both deliberate. The address has to be verified *by Google*,
which is what makes it evidence of ownership. And it has to be confirmed *here*
as well: django-allauth would otherwise settle for an address somebody had
merely claimed without confirming, which would hand them the sign-in of the
person who really owns it. ``SocialAccountAdapter.authenticate_by_email``
enforces the second condition; the first is django-allauth's own.

This is why an account with no confirmed email address is worth chasing: ORCID
does not always pass one on, and without one there is no Google sign-in, no
password sign-in, and no account recovery. The *Connected identities* page says
so when it applies, and the email page warns before the last address is removed
— which is allowed, since the ORCID account still signs the user in.

.. note::

   A password can be set on an account that has no confirmed address, but it
   cannot be used: under mandatory verification django-allauth refuses the
   login and sends a confirmation instead. Setting a password is only useful
   once an address is confirmed.

Which providers a deployment actually offers depends on two things: the
django-allauth provider app has to be in ``INSTALLED_APPS`` (ce-ui registers
ORCID and Google), and a ``socialaccount.socialapp`` row carrying the client
credentials has to exist for it. A provider missing either is simply not shown
on the sign-in page, so the sections below have to be followed for every
provider you want to offer.

.. _orcid-required-for-publication:

ORCID is required for publishing
--------------------------------

Publishing a dataset creates an immutable, citable record with a DOI, and the
authors of such a record have to be identifiable as researchers. TopoBank
therefore refuses to publish for a user who has no ORCID account connected.
Everything else -- uploading, analyzing, sharing -- works with any of the
sign-in methods.

The rule is enforced on the publication endpoints themselves, not only in the
user interface, so it also applies to API clients. The user interface explains
the requirement before a publication form is filled in, and links to the page
where the ORCID account can be connected.

Login with ORCID
----------------

Register a Public API Client
............................

For running TopoBank, you need to register a public API client on the ORCID website
for the following purposes:

- get a client ID + secret in order to be able to authenticate against orcid.org
- set a redirect URL to which TopoBank will redirect after successful authentication

A free ORCID account is enough to register a public API client: there is no
review to pass and no membership to buy. See
`here <https://support.orcid.org/hc/en-us/articles/360006897174>`_ for more
information how to do it.

You need the generated client ID and client secret for the next step.

As redirect URL add all of these

- for development: http://127.0.0.1:8000/accounts/orcid/login/callback/
- for development: http://localhost:8000/accounts/orcid/login/callback/
- for production: https://contact.engineering/accounts/orcid/login/callback/

One of the redirect URLs configured at orcid.org must exactly match the redirect URL, which is
transferred from the TopoBank application during the login process. django-allauth builds that
URL by reversing its callback route, so it always carries the **trailing slash** shown above;
a registered URL without one is rejected as a mismatch.

The host has to match exactly as well, so if you browse to

 http://localhost:8000

i.e. `localhost` instead of `127.0.0.1` during development, you'll need also a redirect url with `localhost` which is

 http://localhost:8000/accounts/orcid/login/callback/

If you have both `localhost` and `127.0.0.1`, it shouldn't matter.


Configure TopoBank with Client ID and Secret Key
................................................

If you use Docker, edit the config files

::

   .envs/.local/.django
   .envs/.production/.django

and set the correct values in the variables
::

   ORCID_CLIENT_ID
   ORCID_SECRET

Adding the ORCID provider with access information
.................................................

In order to connect to the ORCID service, you have to
generate an entry in the local database which holds access information
like a client id and a client secret. This shows the ORCID
website that our site is allowed to use the authentication services of ORCID.

Manually using a database tool or django admin
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

In order to do so, you have several ways. During development you can use an external database tool (e.g. SQLite Browser)
to edit your user account in table `users_user`. Set `is_staff` and `is_superuser` to True.

Enter the URL
::

  localhost:8000/admin

(if in development) and login with your credentials.

Create an entry in the table `socialaccount_socialapp` filling the following fields:
::

    Provider: orcid
    Name: ORCID
    Client ID: <use the one from ORCID website>
    Secret: <use the one from ORCID website>

Recommended: Import database entry via command line tool
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

Use the template file `orcid.yaml.template` which looks like this:
::

    - model: "socialaccount.socialapp"
      pk: 1
      fields:
         provider: orcid
         name: ORCID
         client_id: ${ORCID_CLIENT_ID}
         secret: ${ORCID_SECRET}
         key: ""
         sites: [1]

Copy to `orcid.yaml` and replace `${ORCID_CLIENT_ID}` and `${ORCID_SECRET}` with the corresponding values.
This can be done automatically through environment variables by using the tool `envsubst`:
::

   envsubst < orcid.yaml.template > orcid.yaml

Then this entry must be imported into the database::

   python manage.py loaddata orcid.yaml

See the "Further preparation of first run" section of topobank's ``docs/deploy.rst``
for how to do this in a docker container.

Login with Google
-----------------

Google works the same way: register an OAuth client, then store its credentials
in the database as a second ``socialaccount.socialapp`` entry.

What you need before you start
..............................

An ordinary Google account and a Google Cloud project. Both are free: a Cloud
project needs **no billing account**, because sign-in is not a billable API,
and there is no paid developer programme to join.

Because TopoBank asks only for the ``email`` and ``profile`` scopes (plus
``openid``, which django-allauth adds), which Google classifies as
*non-sensitive*, the app **does not have to pass Google's OAuth verification
review** and needs no third-party security assessment. That changes the moment
a sensitive or restricted scope is added — Gmail, Drive, Calendar and the like
— so do not widen ``SOCIALACCOUNT_PROVIDERS["google"]["SCOPE"]`` without
budgeting several weeks for review.

One piece of validation is required: the domain you enter on the consent
screen has to be one whose ownership you have proven in
`Google Search Console <https://search.google.com/search-console>`_, via a DNS
record or an uploaded file. This is a one-off and takes minutes.

Configure the consent screen
............................

In the Google Cloud console, under *Google Auth Platform* (older versions of
the console call this *APIs & Services* → *OAuth consent screen*), configure:

- user type *External*, since users sign in with their own Google accounts
- the application name and the support and developer contact addresses
- links to the privacy policy and the terms and conditions
- ``contact.engineering`` as an authorized domain (see the domain verification
  above)
- the ``email`` and ``profile`` scopes, and nothing else

.. important::

   A newly configured *External* app starts in publishing status **Testing**,
   which only lets the up-to-100 accounts on its test-user list sign in, and
   **expires every authorization after seven days**. Left in that state,
   sign-in silently stops working for your testers a week later. Press
   *Publish app* to move the app to *In production*; with non-sensitive scopes
   only, that transition does not trigger a review.

If you want TopoBank's name and logo to appear on Google's consent screen
rather than only the domain, complete Google's *brand verification*. It is a
lighter-weight process than scope verification and is not a prerequisite for
sign-in to work.

Register an OAuth client
........................

In the `Google Cloud console <https://console.cloud.google.com/apis/credentials>`_,
create an *OAuth 2.0 Client ID* of type *Web application* and configure its
authorized redirect URIs:

- for development: http://127.0.0.1:8000/accounts/google/login/callback/
- for development: http://localhost:8000/accounts/google/login/callback/
- for production: https://contact.engineering/accounts/google/login/callback/

As with ORCID, the redirect URI must match exactly, including the trailing
slash and the host name you actually browse to. Google exempts ``localhost``
from its HTTPS requirement, so a plain ``http://`` redirect URI is accepted for
development — but ``localhost`` cannot be used as an *authorized domain* on the
consent screen.

The client ID and client secret are shown once the client is created, and can
be downloaded again from the same page afterwards.

Configure TopoBank with Client ID and Secret Key
................................................

Set the variables
::

   GOOGLE_CLIENT_ID
   GOOGLE_SECRET

and import them the same way as for ORCID, using the template file
`google.yaml.template`::

   envsubst < google.yaml.template > google.yaml
   python manage.py loaddata google.yaml

What the site sends by mail
---------------------------

Three mails are part of signing in: confirming an address, resetting a
password, and the reply when a reset is requested for an address no account
holds — which explains that accounts are made with an ORCID iD, since the
reader cannot simply register.

On top of those, ``ACCOUNT_EMAIL_NOTIFICATIONS`` (on here, off in
django-allauth by default) tells a user when the ways of signing in to their
account change: a password set or changed, an address changed or removed, an
identity provider connected or disconnected. A connected provider is a way
*into* the account, so gaining one silently is exactly the event somebody
should hear about. Each names the change, says what to do if it was not them,
and records the address, browser and time it came from.

The templates live in ``ce_ui/templates/account/email/`` and
``ce_ui/templates/socialaccount/email/``. Each mail has a subject, a plain-text
body and an HTML alternative; django-allauth sends the text as the body and
attaches the HTML, and a missing HTML template degrades quietly to a plain
mail, so both belong together. ``base_message`` and ``base_notification`` carry
the design, and the individual mails are a few lines each.

The HTML is written for mail clients rather than browsers: table layout, inline
styles, no stylesheet, no web fonts and no images. A logo would be either an
SVG, which most clients refuse, or a remote image, which many block by default
— both leave a hole where the brand should be — so the wordmark is set in type.

Login with email and password
-----------------------------

Local sign-in needs no provider configuration. It is not a way to *register* —
that is closed — but a way to reach an account that already exists: set a
password from the profile, and the account can then sign in with its username
or with any of its email addresses (``ACCOUNT_LOGIN_METHODS``).

The settings that govern this:

``ACCOUNT_ALLOW_SIGNUP``
   Whether the site accepts registrations for local accounts. ``False`` here,
   because such a registration would create an account with no ORCID iD.
   Switching it on leaves everything else untouched.

``SOCIALACCOUNT_SIGNUP_PROVIDERS``
   The providers that may bring a new account into existence, and which
   therefore cannot be disconnected from one. ``["orcid"]`` here. Set it to
   ``None`` to let any configured provider sign somebody up and every
   connection be removed again.

``ACCOUNT_EMAIL_VERIFICATION``
   Whether a newly added address has to be confirmed before it counts.
   Defaults to ``mandatory``, which requires a working outgoing mail
   configuration. Set it to ``none`` for a development instance that cannot
   send mail.

Note that an address is mandatory for a *local* registration but not for a
social one: ORCID does not necessarily release an email address, and requiring
one would turn a working sign-in into a form to fill in. This is why
``SOCIALACCOUNT_EMAIL_REQUIRED`` is set to ``False`` explicitly — django-allauth
would otherwise derive it from the local signup fields.

.. note::

   A superuser created with ``manage.py createsuperuser`` has no ORCID iD, and
   under mandatory verification it needs a confirmed email address before it
   can sign in with its password. Add one through the Django admin, or set
   ``ACCOUNT_EMAIL_VERIFICATION=none`` while bootstrapping.
