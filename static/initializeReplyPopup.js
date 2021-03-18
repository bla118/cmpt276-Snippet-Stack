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

var editReplyQuill = new Quill('#editReplyEditor', {
    modules: {
        toolbar: {
            container: toolbarOptions
        }
    },
    theme: 'snow'
});

function getUserFromString(x) {
    return x.match('.+: by (.+)')[1].trim();
}

