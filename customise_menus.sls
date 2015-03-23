{% set cantemo_root = "/opt/cantemo/portal" %}
{% set cantemo_plugins = cantemo_root + "/portal/plugins" %}
{% set cantemo_media = cantemo_root + "/portal_media" %}
{% set cantemo_templates = cantemo_root + "/portal_themes/gnm/templates" %}
{% set cantemo_config = "/etc/cantemo/portal/portal.conf" %}

{% set owner_uid = "root" %}
{% set owner_gid = "www-data" %}
{% set module_perm = "0640" %}

patch_menu:
  file.blockreplace:
    - name: {{ cantemo_templates }}/includes/navigation.html
    - marker_start: <li><a href="/roughcuteditor" title="{{ '{%' }} trans "Video editor" {{ '%}' }}">{{ '{%' }} trans "Video editor" {{ '%}' }}</a></li>
    - marker_end: "{{ '{%' }} permissionrequired _collection_read {{ '%}' }}"
    - content: |
        <li><a href="/gnmsyndication/stats/" title="{{ '{%' }} trans "Multimedia Publication Dashboard" {{ '%}' }}">{{ '{%' }} trans "Multimedia Publication Dashboard" {{ '%}' }}</a></li>
