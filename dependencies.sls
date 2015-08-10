{% set owner_uid = "root" %}
{% set owner_gid = "www-data" %}
{% set module_perm = "0644" %}

/opt/cantemo/portal/portal_media/js/chartjs:
  file.recurse:
    - source: salt://gnmplugins/files/static/chartjs
    - exclude_pat: 'E@(\.git|static/)'
    - include_empty: true
    - makedirs: true
    - user: {{ owner_uid }}
    - group: {{ owner_gid }}
    - file_mode: {{ module_perm }}

/opt/cantemo/portal/portal_media/js/codemirror:
  file.recurse:
    - source: salt://gnmplugins/files/static/codemirror
    - exclude_pat: 'E@(\.git|static/)'
    - include_empty: true
    - makedirs: true
    - user: {{ owner_uid }}
    - group: {{ owner_gid }}
    - file_mode: {{ module_perm }}

/opt/cantemo/portal/portal_media/js/knockout-3.3.0.js:
  file.managed:
    - source: salt://gnmplugins/files/static/knockout-3.3.0.js
    - user: {{ owner_uid }}
    - group: {{ owner_gid }}
    - file_mode: {{ module_perm }}

/opt/cantemo/portal/portal_media/js/jquery.cookie.js:
  file.managed:
    - source: salt://gnmplugins/files/static/jquery.cookie.js
    - user: {{ owner_uid }}
    - group: {{ owner_gid }}
    - file_mode: {{ module_perm }}
