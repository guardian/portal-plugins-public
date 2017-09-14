{% set cantemo_root = "/opt/cantemo/portal" %}
{% set cantemo_plugins = cantemo_root + "/portal/plugins" %}
{% set cantemo_media = cantemo_root + "/portal_media" %}
{% set cantemo_templates = cantemo_root + "/portal_themes/gnm/templates" %}
{% set cantemo_config = "/etc/cantemo/portal/portal.conf" %}

{% set owner_uid = "root" %}
{% set owner_gid = "www-data" %}
{% set module_perm = "0640" %}
{% set media_perm = "0644" %}

{{ cantemo_plugins }}/portal.plugins.gnmlibrarytool:
  file.recurse:
    - source: salt://gnmplugins/files/portal.plugins.gnmlibrarytool
    - exclude_pat: 'E@(\.git|static/)'
    - include_empty: true
    - makedirs: true
    - user: {{ owner_uid }}
    - group: {{ owner_gid }}
    - file_mode: {{ module_perm }}

#{{ cantemo_media }}/img/portal.plugins.gnmlibrarytool:
#  file.recurse:
#    - source: salt://gnmplugins/files/portal.plugins.gnmlibrarytool/static
#    - exclude_pat: 'E@(\.git)'
#    - include_empty: true
#    - makedirs: true
#    - user: {{ owner_uid }}
#    - group: {{ owner_gid }}
#    - file_mode: {{ media_perm }}

gnmlibrarytool_sync:
  cmd.run:
    - name: "{{ cantemo_root }}/manage.py migrate"

portal_restart:
  cmd.run:
    - name: "supervisorctl restart all"
