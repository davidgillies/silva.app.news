Copyright (c) 2002 Infrae. All rights reserved.
See also LICENSE.txt

Meta::

  Valid for:  Silva 0.8.x
  Author:     Martijn Faassen
  Email:      faassen@infrae.com
  CVS:        $Revision: 1.1 $

Silva News

  Silva is a Zope-based web application designed for the creation and
  management of structured, textual content. Silva allows users to
  enter new documents as well as edit existing documents using a web
  interface.

  Silva News is an extension to Silva to allow authors to place news- and agendaitems
  on the Silva site and show them on a page. Silva News is a plain Silva add-on which
  can be used on Silva versions 0.8.x and up. No other products are required to use
  Silva News from Silva, besides the products required to run Silva itself.

Installing Silva News

  See INSTALL.txt

Using Silva News

    For the news-application to work, a newsservice must be placed in the Silva-root and called
    'service_news'. This can only be done through the ZMI. You are advised to fill this service
    with some (or preferably all) data before the application is used. The data this service will
    manage is subjects of the newsitems, target audiences of the newsitems and locations for the
    agendaitems. The subject and target audience fields can be used by the filters to filter on
    (so an editor can set up a filter to show only items for a particular subject or target
    audience), the locations will be shown in a pulldown menu when an agendaitem is created
    (together with an option to manually choose a location, so not every possible location has
    to be in this list).

    Next chief-editors can place one or more newssources, which will function as containers to
    place newsitems in. Authors can now fill these sources with news- or a agendaitems. News-
    sources can be set to private, which will make them visible only for newsfilters in the same
    folder as the source. Of course a newsitem will only be found by filters when it is published.

    To control the stream of newsitems across the site, one or more newsfilters (or agendafilters,
    which serve the same purpose) must be placed. In these filters you can choose which
    newssources will be used as the sources and filter out individual newsitems. The placing of
    the filters is supposed to be done by (chief-)editors. Please note that a filter picks up every
    newssource on the site, unless a newssource is explicitly set to private.

    Now authors can place viewers on the places they want to. They can choose which filter(s)
    the viewer uses to get the newsitems from and how many items will be shown. In this setup
    authors have control over where and (more or less) how the newsitems will be shown, and
    (chief-)editors over which items will be shown on the site.

License

  Silva News is released under the BSD license. See 'LICENSE.txt'.
