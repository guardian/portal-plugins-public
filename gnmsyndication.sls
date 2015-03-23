{% set cantemo_root = "/opt/cantemo/portal" %}
{% set cantemo_plugins = "{{ cantemo_root }}/plugins" %}
{% set cantemo_media = "{{ cantemo_root }}/portal_media" %}
{% set cantemo_templates = "{{ cantemo_root }}/portal_themes/gnm/templates" %}
{% set cantemo_config = "/etc/cantemo/portal/portal.conf" %}

{% set owner_uid = "root" %}
{% set ownder_gid = "www-data %}
{% set module_perm = "0640" %}

{{ cantemo_plugins }}/gnmsyndication:
  file.recurse:
    - source: salt://gnm_plugins/files/gnmsyndication
    - exclude_pat: 'E@(\.git)'
    - include_empty: true
    - makedirs: true
    - user: {{ owner_uid }}
    - group: {{ owner_gid }}
    - file_mode: {{ module_perm }}

{{ cantemo_media }}/img/gnmsyndication:
  file.recurse:
    - source: salt://gnm_plugins/files/gnmsyndication/static
    - exclude_pat: 'E@(\.git)'
    - include_empty: true
    - makedirs: true
    - user: {{ owner_uid }}
    - group: {{ owner_gid }}
    - file_mode: {{ module_perm }}
    
patch_menu:
  file.replace:
    - name: {{ cantemo_templates }}/gnm/includes/navigation.html
    - pattern: '<li><a href="/roughcuteditor" title="{% trans "Video editor" %}">{% trans "Video editor" %}</a></li>'
    - repl: |
        <li><a href="/roughcuteditor" title="{% trans "Video editor" %}">{% trans "Video editor" %}</a></li>
        <li><a href="/gnmsyndication/stats/" title="{% trans "Multimedia Publication Dashboard" %}">{% trans "Multimedia Publication Dashboard" %}</a></li>

patch_config:
  file.replace:
    - name: {{ cantemo_config }}
    - pattern: '[homepage_choices]'
    - repl: |
        [homepage_choices]
        /gnmsyndication/stats/ = Multimedia Publication Dashboard

gnmsyndication_sync:
  cmd.run:
    - name: "{{ cantemo_root }}/manage.py migrate"

portal_restart:
  cmd.run:
    - name: "supervisorctl restart all"
