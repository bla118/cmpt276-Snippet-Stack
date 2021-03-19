var animationEvent = whichAnimationEvent();
var currentSnippetEditorIndex; // keeps track of the current snippet being edited
var currentSnippetElement;
var currentReplyElement;
var currentUser;
var viewingComments = false;
var snippets = [];

// the editor for editing snippets
var snippetEditor = new CodeMirror(document.getElementById("editEditor"), {
    lineNumbers: true,
    autoRefresh: true,
    theme: 'dracula'
});
snippetEditor.refresh();

// returns animation event
function whichAnimationEvent(){
    var t,
        el = document.createElement("fakeelement");

    var animations = {
    "animation"      : "animationend",
    "OAnimation"     : "oAnimationEnd",
    "MozAnimation"   : "animationend",
    "WebkitAnimation": "webkitAnimationEnd"
    }

    for (t in animations){
    if (el.style[t] !== undefined){
        return animations[t];
    }
    }
}

// highlight the code blocks in the node
function highlightCodeBlocks(node) {
    // highlight code blocks
    var replies = node.getElementsByTagName("pre");

    Array.from(replies).forEach((block) => {
    hljs.highlightBlock(block);
    });
    
}

// helper
function getLanguageFromString(lang) {
    // var re = lang.match('([^:]+):.*')[1].trim();
    switch (lang) {
    case 'c':
    case 'c++': 
    case 'c#':
    case 'objective-c': 
    case 'java': 
    case 'kotlin': 
    case 'ceylon':
    case 'scala': 
        return 'clike';
        break;

    case 'html': 
        return 'htmlmixed';
        break;

    case 'python':
        return 'python';
        break;
        
    default:
        return lang;
    }
}


// creates a new editor
function appendSnippetEditor(block, lang, code) {
    let editor = new CodeMirror(block, {
    mode: lang,
    lineNumbers: true,
    readOnly: "nocursor",
    theme: 'dracula'
    });
    editor.setValue(code);
    editor.refresh();
    snippets.push(editor);
}

// create replies container
function makeCommentContainer(id, comment, owner, user) {
    var post = document.createElement('div');
    post.id = id;
    post.className = "post-section";
    var header = document.createElement('div');
    header.className = "flex-reply-header";
    var container = document.createElement('div');
    container.className = 'reply-username';
    container.innerHTML = `<i class="fa fa-user" aria-hidden="true" style="margin-right: 5px;"></i>${owner}`;
    header.appendChild(container);
    post.appendChild(header);

    var body = document.createElement('div');
    body.className = 'reply-body';
    body.id = `${id}_raw`;
    body.innerHTML = comment;
    post.appendChild(body);

    var footer = document.createElement('div');
    footer.className = "flex-reply-footer";
    if (owner == user) {
    var editButton = document.createElement('button');
    editButton.type = 'button';
    editButton.className = "btn btn-link";
    editButton.dataset.toggle = "modal";
    editButton.dataset.target = "#editReplyModal";
    editButton.addEventListener('click', function() {
        console.log(body.innerHTML);
        editReplyQuill.root.innerHTML = body.innerHTML;
        currentReplyElement = post;
    });
    editButton.innerHTML = `<i class="fa fa-pencil" aria-hidden="true"></i>Edit`;
    footer.appendChild(editButton);
    }

    // var likesButton = document.createElement('button');
    // likesButton.type = 'button';
    // likesButton.className = "btn btn-link";
    // likesButton.addEventListener('click', async function() {
    //   this.disabled = true;

    //   var x = parseInt(likes, 10) + 1;
    //   data = {};
    //   data['likes'] = x;

    //   event.preventDefault(); // dont refresh: front end will dynamically change value
    //   // make a call to the backend to update database
    //   let res = await fetch(urlForLikes, {method: 'POST', body: JSON.stringify(data)});
    //   if (res.status != 400) {
    //     // increment likes
    //     this.nodeValue = x;
    //   }
    // });
    // likesButton.innerHTML = `${likes}<i class="fa fa-thumbs-up" aria-hidden="true" style="margin: 5px;"></i>`;
    
    // footer.appendChild(likesButton);
    post.appendChild(footer);

    document.getElementById('active').appendChild(post);
}

// create a snippet container
function makeSnippetContainer(id, lang, name, owner, likes, user, i) {
    var s = document.createElement('div');
    s.className = "flex-snippet";
    s.id = id;

    // header
    var header = document.createElement('div');
    header.className = "snippet-header";
    var title = document.createElement('div');
    title.className = "snippet-title";
    var tn = document.createElement('span');
    tn.style.color = "rgb(64, 67, 240)"
    tn.appendChild(document.createTextNode(name));
    title.appendChild(tn);
    var tl = document.createElement('small');
    tl.style.color = "#a8a7a7";
    tl.appendChild(document.createTextNode(lang));
    title.appendChild(tl);
    var tu = document.createElement('small');
    tu.appendChild(document.createTextNode(owner));
    title.appendChild(tu);

    header.appendChild(title);

    s.appendChild(header);

    if (owner == user) {
    let trashButton = document.createElement('button');
    trashButton.type = "button";
    trashButton.className = "btn btn-link view-replies-btn";
    trashButton.style.color = "red";
    // delete button
    header.appendChild(trashButton);

    trashButton.addEventListener('click',   async function() {
        if (confirm("Are you sure you want to delete this snippet?")) {

        // delete the code display for that snippet
        snippets.splice(i, 1);

        s.classList.add('deletedSnippetAnimation');
        $(this).parent().parent().one(animationEvent, async function() {
            $(this).remove();
            
            if (snippets.length == 0) {
            $('#snippet-display').html("<h1 style=\"width: 100%; text-align: center;\">No more snippets!</h1>");
            }

            var data = {};
            data['idToDel'] = id;
            // make a call to the backend to update database
            const response = await fetch(urlForDelete,
                                    {method: 'POST', body: JSON.stringify(data)});

            if (viewingComments) {
            var node = document.getElementById('active');
            while (node.firstChild) {
                node.removeChild(node.lastChild);
            }
            }
        });
        }
    });
    trashButton.innerHTML = "<i class=\"fa fa-trash\" aria-hidden=\"true\"></i>";
    }

    // body
    var body = document.createElement('div');
    body.className = "snippet-body";
    body.id = `${id}_raw`;

    s.appendChild(body);

    // footer
    var footer = document.createElement('div');
    footer.className = "snippet-footer";
    var container = document.createElement('div');
    var viewCommentsButton = document.createElement('button');
    viewCommentsButton.type = "button";
    viewCommentsButton.className = "btn btn-link view-replies-btn";
    viewCommentsButton.addEventListener('click', async function() {

        viewingComments = true;
        var data = {};
        data['snippet_id'] = id;

        // make a get call to the backend
        let response = await fetch(urlForGettingComments, {method: 'POST', body: JSON.stringify(data)});
        let res = await response.json();

        // remove all children except this
        $("#snippet-display").children(`:not(#${id})`).remove();

        if (res) {
            for (r of res) {
                makeCommentContainer(r[0], r[2], r[1], user);
            }
            // redirect to active.html
            // let endpoint = "{{ url_for('activePage') }}"
            // window.location.replace(baseURL + endpoint);
            highlightCodeBlocks(document.getElementById("active"));
            $(this).remove();
        } else {
            alert("No comments for this snippet!");
        }

    });

    viewCommentsButton.appendChild(document.createTextNode("View Replies"));
    container.appendChild(viewCommentsButton);
    var commentButton = document.createElement('button');
    commentButton.type = "button";
    commentButton.className = "btn btn-link";
    commentButton.dataset.toggle = "modal";
    commentButton.dataset.target = "#replyModal";
    commentButton.addEventListener('click', function() {
    currentSnippetElement = s;
    });
    commentButton.appendChild(document.createTextNode("Comment"));

    container.appendChild(commentButton);


    if (user == owner) {
    let editButton = document.createElement('button');
    editButton.type = 'button';
    editButton.className = "btn btn-link";
    editButton.dataset.toggle = "modal";
    editButton.dataset.target = "#editModal";
    editButton.addEventListener('click',   function() {
        snippetEditor.setOption("mode", getLanguageFromString(lang));
        console.log(getLanguageFromString(lang));

        // copy value into snippet text editor
        snippetEditor.setValue(snippets[i].getValue());
        // save the index for form submission
        currentSnippetEditorIndex = i;
        currentSnippetElement = s;
    });
    editButton.innerHTML = `<i class="fa fa-pencil" aria-hidden="true"></i>Edit`;
    container.appendChild(editButton);
    }

    footer.appendChild(container);
    var likesButton = document.createElement('button');
    likesButton.type = "button";
    likesButton.className = "btn btn-link";
    likesButton.addEventListener('click', async function(event) {
    event.preventDefault(); // dont refresh: front end will dynamically change value

    this.disabled = true;

    console.log(this.firstChild);
    console.log(this.firstChild.nodeValue);
    var likes = parseInt(this.firstChild.nodeValue, 10) + 1;
    var data = {};
    data['snippet_id'] = id;

    // make a call to the backend to update database
    let res = await fetch(urlForLikes, {method: 'POST', body: JSON.stringify(data)});
    if (res.status != 400) {
        // increment likes
        this.firstChild.nodeValue = likes;
    }
    });
    likesButton.innerHTML = `${likes}<i class="fa fa-thumbs-up" aria-hidden="true" style="margin: 5px;"></i>`
    footer.appendChild(likesButton);
    
    s.appendChild(footer);

    return [s, body];
}

// posting a comment
document.getElementById("reply-form").addEventListener('submit', async function (event) {
    event.preventDefault();
    // get form values
    data = {};
    var comment = replyQuill.root.innerHTML;
    if (!comment) {
        alert("Comment is empty! Cannot submit empty comment!");
        return false;
    }
    data['comment_text'] = comment;
    data['snippet_id'] = currentSnippetElement.id;
    var user = currentSnippetElement.getElementsByClassName("snippet-title")[0].innerHTML;

    data['username'] = document.getElementById("snippet-display").firstElementChild.firstElementChild.firstElementChild.lastElementChild.innerHTML;

    // make a call to the backend to update database
    let response = await fetch(urlForComments, {method: 'POST', body: JSON.stringify(data)});
    // console.log(replyQuill.root.innerHTML);
    let res = await response.json();
    console.log(res);
    // display the comment to the screen
    if (viewingComments) {
        makeCommentContainer(res, comment, currentUser, currentUser);
    }

    $('#replyModal').modal('hide');
    this.reset();
    replyQuill.root.innerHTML = "";
});

// submit edited reply handler
document.getElementById("edit-reply-form").addEventListener('submit', async function(event) {
    event.preventDefault();

    var update = editReplyQuill.root.innerHTML;

    currentReplyElement.children[1].innerHTML = update;
    if (!update) {
        alert("Comment is empty! Cannot submit empty comment!");
        return false;
    }

    var data = {};
    data['comment_id'] = currentReplyElement.id;
    data['edited_comment'] = update;
    let res = await fetch(urlForEditComment, {method: 'POST', body: JSON.stringify(data)});

    $('#editReplyModal').modal('hide');
    this.reset();
    editReplyQuill.root.innerHTML = "";

    // highlight code in pre blocks
    highlightCodeBlocks(currentReplyElement);
});

// submit updated snippet
document.getElementById("submitUpdatedSnippet").addEventListener('submit', async function(event) {
        event.preventDefault();

        // get the code from the editor
        // copy the code into the current snippet
        var data = {};
        var contents = snippetEditor.getValue();
        console.log(typeof(contents));
        console.log(contents);
        if (!contents) {
        alert("Snippet is empty! Cannot submit empty snippet!");
        return false;
        }

        data['edited_code'] = contents;
        data['snippet_id'] = currentSnippetElement.id;

        // make a call to the backend to update database
        let res = await fetch(urlForEditSnippet, {method: 'POST', body: JSON.stringify(data)});

        snippets[currentSnippetEditorIndex].setValue(contents);
        $('#editModal').modal('hide');
    });
