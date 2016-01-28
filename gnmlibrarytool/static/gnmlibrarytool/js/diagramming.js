
function iterate_query(rules, container, prefix){
    console.log("prefix: " + prefix);

    $.each(rules, function(idx, r) {
        console.log(r)
        if(r['type']=='field'){
            var box = $("<div>", {'id': prefix + '_r' + idx, 'class': 'rule_box'});
            container.append(box);
            box.append($("<p>", {'class': 'field_name'}).html(r['name']))
            val_list = $("<ul>", {'class': 'rule_list'});
            $.each(r['values'], function(idx,v){
                val_list.append($("<li>", {'class': 'rule_list'}).html(v))
            });
            box.append(val_list);
            console.log(box);
        } else if(r['type']=='operator'){
            var box = $("<div>", {'id': prefix + '_r' + idx, 'class': 'operator_box'});
            container.append(box);
            box.append($("<p>", {'class': 'operator_type'}).html(r['operation']))
            var members_box = $("<div>", {'id': prefix + '_r' + idx + '_members', 'class': 'operator_members'});
            box.append(members_box);
            iterate_query(r['members'], members_box, prefix + '_o' + idx);
        } else {
            console.log("type of " + r['type'] + " is not implemented");
        }
    });
}

function iterate_rules(rules, container, prefix){

    $.each(rules, function(key, r) {
        console.log(r);
        var box = $("<div>", {'id': prefix + '_s_' + key, 'class': 'storage_box'});
        container.append(box);
        box.append($("<p>", {'class': 'tag_name'}).html(key));
        box.append($("<p>", {'class': 'precedence prio_' + r['precedence']}).html(r['precedence']));
        box.append($("<p>", {'class': 'storage_count'}).html("Storage count: " + r['count']));
        box.append($("<p>", {'class': 'subtitle'}).html("Include"))
        var exclude_box = $("<ul>", {'class': 'rule_list'});
        $.each(r['include'], function(idx,v){
            exclude_box.append($("<li>").html(v))
        });
        box.append(exclude_box);

        box.append($("<p>", {'class': 'subtitle'}).html("Exclude"))
        var exclude_box = $("<ul>", {'class': 'rule_list'});
        $.each(r['exclude'], function(idx,v){
            exclude_box.append($("<li>").html(v))
        });
        box.append(exclude_box);

    });
}

function throbber(libid){
    rtn = $("<div>", {'id': 'throbber_' + libid, 'class': 'throbber'});

    rtn.append($("<img>", {'src': '/sitemedia/load.gif', 'alt': "Loading " + libid, 'style': 'float: left;'}));
    rtn.append($("<p>", {'class': 'throbber_caption' }).html("Loading " + libid + "..."));

    return rtn;
}

function draw_diagram(parent, baseurl, libid, sourcestr){
    var container=$("<div>", {'id': "diagram_" + libid, 'class': 'diagram_container'})
    parent.append(container);

    container.append(throbber(libid));

    $.getJSON(baseurl + '/diagram/library/' + libid, function(data){
        console.log(data);

        container.empty();

        var info_column=$("<div>", {'id': "diagram_" + libid + "_info", 'class': 'info_column'})
        container.append(info_column);

        var field_column=$("<div>", {'id': "diagram_" + libid + "_fields", 'class': 'field_column'})
        container.append(field_column);
        var rule_column=$("<div>", {'id': "diagram_" + libid + "_rule", 'class': 'rule_column'})
        container.append(rule_column);

        var info_box=$("<div>", {'id': "diagram_" + libid + "_infobox", 'class': 'info_box'});
        info_column.append(info_box);
        str = "<h1 class='library_nick'>" + data['data']['nickname'] + "</h1>";
        str += "<p class='library_id'>" + data['data']['id'] + "</p>";
        str += "<p class='library_hitcount'>Currently able to affect " + data['data']['hits'].toLocaleString() + " items</p>";
        if(sourcestr){
            str += "<p class='library_source'>" + sourcestr + "</p>";
        }
        info_box.append(str);
        //container.append('<h1>test</h1>')
        iterate_query(data['data']['query'], field_column, "diagram");
        iterate_rules(data['data']['rules'], rule_column, "rule")
    }).fail(function(jqXHR, textStatus, errorThrown){
        console.log(errorThrown);
        container.empty();
        container.append($("<p class='error'>Unable to load " + libid + ": " + errorThrown + "</p>"));
    });
}