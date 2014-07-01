
function toTitleCase(str)
{
    return str.replace(/([^\W_]+[^\s-]*) */g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

function error_message(msg, category)
{
    $("#message-container").append(
            '<div class="flashed_msg">' +
            '<div class="alert alert-' + category + ' alert-dismissable fade in">' +
            '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' +
            '<strong>' + toTitleCase(category) + ': </strong>' + msg +
            '</div>' +
            '</div>')
}

function get_api_record(model, model_id, callback)
{
    // retrieve JSON record from API
    $.ajax(API_HOST + model + "/" + model_id + "/")
        .done(function(data){
            callback(data)
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            var msg = "empty response"
            if(jqXHR.responseText)
            {
                msg = jqXHR.responseText
                if(msg.length > 100)
                    msg = msg.substring(0,100);
            }
            error_message("Error retrieving record from server. [" + msg + "]", "warning");
        })
}

// enable modal windows
function show_modal(title, body)
{
    $("#page-modal-title").html(title);
    $("#page-modal-body").html(body);
    $("#page-modal").modal({'show': true});
}

function readable_attr(attr_name)
{
    return toTitleCase(attr_name.replace("_", " "))
}

function map_model_to_modal(model, title_attr, display_attrs)
{
    var title = model[title_attr]
    var body = ""

    for (var i=0; i<display_attrs.length; i++)
    {
        console.log(model[display_attrs[i]])
        if(model[display_attrs[i]])
        {
            var key = display_attrs[i]
            var value = model[display_attrs[i]]
            body += readable_attr(key) + " " + value + "<br>"
        }
    }
    show_modal(title, body)
}

function show_supplier_modal(supplier_id)
{
    var attrs = [
        'street_address',
        'website',
        'contact',
        'phone',
        'alt_phone',
        'fax',
        'email',
        'alt_email',
        'added_by'
    ]
    get_api_record('supplier', supplier_id, function(supplier){
        map_model_to_modal(supplier, 'name', attrs)
    })
}

function show_manufacturer_modal(manufacturer_id)
{
    var attrs = [
        'name',
    ]
    get_api_record('manufacturer', manufacturer_id, function(manufacturer){
        // flatten record
        if(manufacturer.country)
        {
            console.log(manufacturer.country)
            attrs.push('country_name')
            manufacturer['country_name'] = manufacturer.country.name
        }
        map_model_to_modal(manufacturer, 'name', attrs)
    })
}

$(document).ready(function(){

    // enable tooltips
    $(".tooltip-enabled").tooltip({});

    function medicine_matcher(){
        return function findMatches(query, callback) {
            medicines = [];
            $.get(API_HOST + 'autocomplete/' + query + '/', function(data){
                callback(data);
            },'json');
        };
    }

    // handle search
    $("#search-box").typeahead({
            hint: true,
            highlight: true,
            minLength: 1
        },
        {
            name: 'medicines',
            displayKey: 'name',
            source: medicine_matcher()
        })
        .on('typeahead:selected', function(e, datum){
            window.location = '/medicine/' + (datum["medicine_id"]) + '/';
        }
    );
    $('#search-box.input-lg').siblings('input.tt-hint').addClass('hint-large');

    $("#search-box").focus()

});