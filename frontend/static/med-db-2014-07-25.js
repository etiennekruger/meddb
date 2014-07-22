
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
            '</div>');
}