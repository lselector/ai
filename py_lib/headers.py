# -*- coding: utf-8 -*-
"""
# http_headers.py
# ---------------------------------------------------------------
"""

import os
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"
import sys

# ---------------------------------------------------------------
def headers_list():
    """
    # returns a list of headers.
    # each header is a dictionary
    # headers were collected by going (in different browsers) to this link:
    #     https://www.proxyrain.com/echo.xml
    # then adding fields "DNT", "Cache-Control", "Referer"
    """
    list_win = []

    list_win += [           # Firefox on Windows 7
        { "Accept"          : "text/html, application/xhtml+xml, */*",
          "User-Agent"      : "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
          "Accept-Encoding" : "gzip, deflate",
          "Accept-Language" : "en-US"
        }
        ]

    list_win += [           # Chrome on Windows 7
        { "Accept"          : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
          "User-Agent"      : "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
          "Accept-Encoding" : "gzip, deflate", # removed sdch, br
          "Accept-Language" : "en-US,en;q=0.8"
        }
        ]

    list_win += [           # Firefox on Windows 10 (Lev home)
        { "Accept"          : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
          "User-Agent"      : "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0",
          "Accept-Encoding" : "gzip, deflate",  # removed br
          "Accept-Language" : "en-US,en;q=0.5",
          "Upgrade-Insecure-Requests" : "1"
        }
        ]

    list_win += [           # Chrome on Windows (George)
        { "Accept"          : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
          "User-Agent"      : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
          "Accept-Encoding" : "gzip, deflate", # removed sdch, br
          "Accept-Language" : "en-US,en;q=0.8",
          "Upgrade-Insecure-Requests" : "1"
        }
        ]

    list_win += [           # IE on Windows (George)
        { "Accept"          : "text/html,application/xhtml+xml,*/*",
          "User-Agent"      : "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
          "Accept-Encoding" : "gzip, deflate",
          "Accept-Language" : "en-US"
        }
        ]

    list_win += [           # Firefox on Windows (George)
        { "Accept"          : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
          "User-Agent"      : "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0",
          "Accept-Encoding" : "gzip, deflate",  # removed br
          "Accept-Language" : "en-US,en;q=0.5",
          "Upgrade-Insecure-Requests" : "1"
        }
        ]

    list_win += [           # Chrome on Windows (Yechiel)
        { "Accept"          : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
          "User-Agent"      : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
          "Accept-Encoding" : "gzip, deflate", # removed sdch, br
          "Accept-Language" : "en-US,en;q=0.8",
          "Upgrade-Insecure-Requests" : "1"
        }
        ]

    list_win += [           # IE on Windows (Yechiel)
        { "Accept"          : "text/html,application/xhtml+xml,*/*",
          "User-Agent"      : "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
          "Accept-Encoding" : "gzip, deflate",
          "Accept-Language" : "en-US"
        }
        ]

    list_win += [           # Firefox on Windows (Yechiel)
        { "Accept"          : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
          "User-Agent"      : "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
          "Accept-Encoding" : "gzip, deflate",  # removed br
          "Accept-Language" : "en-US,en;q=0.5"
        }
        ]

    list_win += [           # Chrome on Windows (Dan)
        { "Accept"          : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
          "User-Agent"      : "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
          "Accept-Encoding" : "gzip, deflate", # removed sdch, br
          "Accept-Language" : "en-US,en;q=0.8",
          "Upgrade-Insecure-Requests" : "1"
        }
        ]

    list_win += [           # IE on Windows (Dan)
        { "Accept"          : "text/html, application/xhtml+xml, */*",
          "User-Agent"      : "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
          "Accept-Encoding" : "gzip, deflate",
          "Accept-Language" : "en-US"
        }
        ]

    list_mac = []

    list_mac += [           # Lev-s Mac Chrome ??
        { "Accept"          : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
          "User-Agent"      : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
          "Accept-Encoding" : "gzip, deflate", # removed sdch, br
          "Accept-Language" : "en-US,en;q=0.8"
        }
        ]

    list_mac += [           # Brad-s Mac Chrome
        { "Accept"          : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
          "User-Agent"      : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36",
          "Accept-Encoding" : "gzip, deflate", # removed sdch, br
          "Accept-Language" : "en-US,en;q=0.8",
          "Upgrade-Insecure-Requests" : "1"
        }
        ]

    list_mac += [          # Brad-s Mac Safari
        { "Accept"          : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
          "User-Agent"      : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.7",
          "Accept-Encoding" : "gzip, deflate",
          "Accept-Language" : "en-us"
        }
        ]

    # combine lists together
    mylist = list_win + list_mac

    # add extra fields to all headers
    # for ii in range(len(mylist)):
    #     mylist[ii]["DNT"          ] = "1"
    #     mylist[ii]["Cache-Control"] = "no-cache"
    #     mylist[ii]["Referer"      ] = "https://www.google.com"

    return mylist
