// toolbar
var toolbarOptions = [
    [{'header': []}, 'bold', 'italic', 'underline', 'strike', {'script': 'sub'}, {'script': 'super'}], 
    [{'color': []}, {'background': []}], 
    ['blockquote', 'code-block'], [{'list': 'ordered'}, {'list': 'bullet'}], 
    ['link', 'image']
    ];

// for the quill editor
var replyQuill = new Quill('#replyEditor', {
    modules: {
        toolbar: {
            container: toolbarOptions
        }
    },
    theme: 'snow'
});

var currentReplySnippetID;

function addReply() {
    currentReplySnippetID = event.currentTarget.parentNode.parentNode.parentNode.id;
}

function getUserFromString(x) {
    return x.match('.+: by (.+)')[1].trim();
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
    data['snippet_id'] = currentReplySnippetID;
    var user = document.getElementById(currentReplySnippetID).getElementsByClassName("snippet-title")[0].innerHTML;
    data['username'] = getUserFromString(user);

    // make a call to the backend to update database
    let res = await fetch(urlForComments, {method: 'POST', body: JSON.stringify(data)});
    // console.log(replyQuill.root.innerHTML);
    $('#replyModal').modal('hide');
    this.reset();
    replyQuill.root.innerHTML = "";
});
