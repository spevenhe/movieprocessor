
var last_refresh_dic = new Array()

function getpostlist(id){
    var last = last_refresh_dic[id]
    $.ajax({
        url:"/movie_processor/refresh/"+id,
        type: "POST",
        data:{
            "last_refresh":last,
            "id":id,
            "csrfmiddlewaretoken":getCSRFToken(),
        },
        dataType : "json",
        success: updatepostlist
    });
}


function updatepostlist(posts) {
    user_status = posts[posts.length-1]['status'];
    posts.pop();
    last_refresh = posts[posts.length-1]['lastupdatetime'];
    posts.pop();
    movie_id = posts[posts.length-1]['movie_id'];
    posts.pop();
    last_refresh_dic[movie_id] = last_refresh
    comments = posts[posts.length-1]['comments'];
    posts.pop();
    var list = document.getElementById("post_stream"); 
    for (var i = 0; i < posts.length; i++) {
        // Extracts the item id and text from the response
        var id = posts[i]["pk"];  // pk is "primary key", the id
        var post_text = posts[i]["fields"]["text"];
        var user_id = posts[i]["fields"]["user"];
        var post_name = posts[i]["fields"]["username"];
        var post_time = posts[i]["fields"]["post_time"];

        // Builds a new HTML list item for the todo-list item
        var newItem = document.createElement("tr");
        newItem.setAttribute("id", "post_div_"+id);
        if(user_status){
            newItem.innerHTML ="<p class='alert alert-warning my-3 p-1 col-18 shadow-sm'>Post by <a href='/movie_processor/profile/"+user_id+
            "' id='id_post_profile_"+id+"'>"+post_name+"</a> -- "+
            "<span id='id_post_text_"+id+"'>" +sanitize(post_text) +
            "</span> <span class='text-centers' id='id_post_date_time_"+id+
            "'> -- " + dateFormat(post_time) +"</span></p>"+
            "<ul class='list-unstyled alert alert-light text-dark' id='id_comment_list_"+id+
            "'><li>"+
            "<div class='input-group'><div class='input-group-prepend'>"+
            "<button class='btn btn-outline-warning btn-sm' type='button'>comment</button></div>"+
            "<input class='form-control col-6' aria-describedby='basic-addon1' type='text' id='id_comment_text_input_"+id+"'>"+
            "<div class='input-group-append'><button class='btn btn-outline-warning btn-sm' type='button' onclick='addcomment("+id+","+movie_id+")' id='id_comment_button_"+id+"'>submit</button>"+
            "</li></ul>";
        }
        else{
            newItem.innerHTML ="<p class='alert alert-warning my-3 p-1 col-18 shadow-sm'>Post by <a href='/movie_processor/profile/"+user_id+
            "' id='id_post_profile_"+id+"'>"+post_name+"</a> -- "+
            "<span id='id_post_text_"+id+"'>" +sanitize(post_text) +
            "</span> <span class='text-centers' id='id_post_date_time_"+id+
            "'> -- " + dateFormat(post_time) +"</span></p>"+
            "<ul class='list-unstyled alert alert-light text-dark' id='id_comment_list_"+id+
            "'></ul>";
        }
        
        list.prepend(newItem);
    }
    
    for (var i = 0; i < comments.length; i++){
        var comment_id = comments[i]["pk"];  // pk is "primary key", the id
        var comment_text = comments[i]["fields"]["text"];
        var comment_user_id = comments[i]["fields"]["user"];
        var post_id = comments[i]["fields"]["post_id"];
        var comment_name = comments[i]["fields"]["username"];
        var comment_time = comments[i]["fields"]["comment_time"];

        var comment_div = document.getElementById("id_comment_list_"+post_id);
        
        var newItem = document.createElement("li");
        newItem.setAttribute("id", "id_comment_list_div_"+comment_id);

        if(user_status){
            newItem.innerHTML ="<i>Comment by <a href='/movie_processor/profile/"+comment_user_id+
            "'id='id_comment_profile_"+comment_user_id+"'>"+comment_name+"</a> -- </i>"+
            "<span id='id_comment_text_"+comment_id+"'>" +sanitize(comment_text) +
            "</span> <span class='text-centers' id='id_comment_date_time_"+comment_id+
            "'>--" + dateFormat(comment_time) +"</span>";
        }
        else{
            newItem.innerHTML ="<i>Comment by <a href='/movie_processor/profile/"+comment_user_id+
            "'id='id_comment_profile_"+comment_user_id+"'>"+comment_name+"</a> -- </i>"+
            "<span id='id_comment_text_"+comment_id+"'>" +sanitize(comment_text) +
            "</span> <span class='text-centers' id='id_comment_date_time_"+comment_id+
            "'> -- " + dateFormat(comment_time) +"</span><br/>";
        }
        comment_div.appendChild(newItem);
    } 
}

function dateFormat(date_ori){
    var date = new Date(date_ori);
    var yyyy = date.getFullYear();
    var dd = date.getDate();
    var mm = date.getMonth()+1;
    var HH = date.getHours();
    var MM = date.getMinutes();
    var ampm = HH >= 12 ? 'p.m.' : 'a.m.';
    HH = HH % 12;
    HH = HH ? HH : 12; // the hour '0' should be '12'
    MM = MM < 10 ? '0'+MM : MM;
    var sol = new String(mm+"/"+dd+"/"+yyyy+" "+HH+":"+MM+" "+ampm);
    return sol;
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
}

function getCSRFToken() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        c = cookies[i].trim();
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length);
        }
    }
    return "unknown";
}


function displayError(message) {
    var errorElement = document.getElementById("error");
    errorElement.innerHTML = message;
}

function addpost(id) {
    var posttextElement = $("#id_post_text");
    var posttextValue   = posttextElement.val();
    posttextElement.val('');
    displayError('');
    $.ajax({
        url: "/movie_processor/add_post",
        type: "POST",
        data: "post="+posttextValue+"&id="+id+"&csrfmiddlewaretoken="+getCSRFToken(),
       
        dataType : "json",
        success: function(response) {
            if (Array.isArray(response)) {
                getpostlist(id);
            } else {
                displayError(response.error);
            }
        }
    });
}

function getpage(page){
    var searchElement = document.getElementById('id_keywords');
    var searchValue = searchElement.innerHTML;
    scrollTo(0,0);
    $.ajax({
        url: "/movie_processor/search_ajax",
        type: "POST",
        data: "search_content="+searchValue+"&page="+page+"&csrfmiddlewaretoken="+getCSRFToken(),
        dataType: "json",
        success: updatemovielist
    });
} 
  
function addcomment(post_id,movie_id) {
    var comment_list_id = '#id_comment_text_input_' + post_id;
    var commenttextElement = $(comment_list_id);
    var commenttextValue   = commenttextElement.val();
    commenttextElement.val('');
    displayError('');
    $.ajax({
        url: "/movie_processor/add_comment",
        type: "POST",
        data: "comment="+encodeURIComponent(commenttextValue)+"&csrfmiddlewaretoken="+getCSRFToken()+"&post_id="+encodeURIComponent(post_id)+"&movie_id="+encodeURIComponent(movie_id),
        dataType : "json",
        success: function(response) {
            if (Array.isArray(response)) {
                getpostlist(movie_id);
            } else {
                displayError(response.error);
            }
        }
    });
}



function updatemovielist(posts){

    var list = document.getElementById("movie-list");
    while(list.hasChildNodes()){
        list.removeChild(list.firstChild);
    }

    var search_content = posts[posts.length-1]['search_content'];
    posts.pop();
    var current_page = posts[posts.length-1]['current_page'];
    posts.pop();
    var total_page = posts[posts.length-1]['page_number'];
    posts.pop();


    document.getElementById('id_keywords').innerHTML = search_content;
    $(posts).each(function(){
        $("#movie-list").append(
            "<div class='media text muted pt-3'>"+
            "<table><tr>"+
            "<td rowspan='2'><div><img src="+this.fields.poster+"hright='200' width='120'></div></td>"+
            "<td>"+
            "<a href='movie/"+this.pk+"'><h4 class='movie-title'>"+this.fields.name+"</h4></a><h6>"+this.fields.release_time+"&nbsp;"+this.fields.movie_length+"</h6>"+
            "<h6 class='tags'>Tags:<span class='badge badge-secondary'>"+this.fields.movie_type+"</span></h6>"+
            "<div class='Introduction'"+this.fields.storyline+"</div>"+
            "<div class='cast'>Director:"+this.fields.director+"</div>"+
            "<div class='cast'>Stars:"+this.fields.star+"</div>"+
            "</td></tr></table></div>"
        );
    });
    var current = document.getElementById("current-page");
    current.innerHTML = "Page"+current_page+"of"+total_page;
}


function autoSearch(){
    var name_ele = $("#enterName");
    var name_str = name_ele.val();
    $.ajax({
        url: "/movie_processor/auto_search",
        type: "GET",
        data: "search_name="+name_str+"&csrfmiddlewaretoken="+getCSRFToken(),
        dataType: "json",
        success: updateautolist
    });
}

function updateautolist(posts){
    var list = document.getElementById("result");
    while(list.hasChildNodes()){
        list.removeChild(list.firstChild);
    }

    $(posts).each(function(){
        $("#result").append(
            "<tr>"+
            "<td class='movie-title title-cell' style='list-style-type:none'><a href='/movie_processor/movie/"+
            this.pk+"'>"+this.fields.name+"</td></a>"+
            "<td class='tags cast text-white direct-cell'>"+"<h6 class='badge badge-secondary'>"+this.fields.director+"</h6></td>"+
            "<td class='tags cast text-white type-cell'>"+"<h6 class='badge badge-secondary'>"+this.fields.movie_type+"</h6></td>"+
            "</tr>"
        )
    });
};

function first_load(){
    var movie_idElement = document.getElementById("movie_id");
    var movie_id = movie_idElement.attributes["value"].value;
    getpostlist(parseInt(movie_id));
};


window.onload = first_load;
