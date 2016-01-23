httpie-akamai
=============

`HTTPie <https://github.com/jkbr/httpie>`_ plugin to help with testing sites hosted on the Akamai content delivery network.

**Note: this software is not provided or endorsed by Akamai Technologies**

This will plugin will add standard Akamai debugging headers to the request, and colorize Akamai informational headers in the response.

Optionally, the request can be forced to the Akamai production or staging networks (if the public hostname is the same as the edge hostname).

Installation
------------

.. code-block:: bash

    $ pip install httpie-akamai

You should now see ``hmac`` under ``--auth-type`` in ``$ http --help`` output.

Usage
-----

Prefix the URL with ak-, akp- or aks- to activate the plugin. The plugin handles URLs starting with "ak" as an alternative schema.

Use ak- to activate debugging headers and syntax coloring without changing the request target:

.. code-block:: bash

    $ http -pHh ak-http://www.example.com/

Use akp- and aks- to force the request onto the Akamai production or staging network respectively. This only works if the public hostname and the edge hostname are the same.

.. code-block:: bash
    $ http -pHh akp-http://www.example.com
    # is equivalent to
    $ http -pHh http://www.example.com.edgesuite.net Host:www.example.com

    $ http aks-http://www.example.com
    # is equivalent to
    $ http -pHh http://www.example.com.edgesuite-staging.net Host:www.example.com
