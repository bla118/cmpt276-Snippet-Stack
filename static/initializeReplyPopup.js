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

// posting a comment
document.getElementById("reply-form").addEventListener('submit', async function (event) {
    event.preventDefault();
    // get form values
    var data = replyQuill.root.innerHTML;

    // make a call to the backend to update database
    let res = await fetch(urlForComments, {method: 'POST', body: JSON.stringify(data)});
    // console.log(replyQuill.root.innerHTML);
    $('#replyModal').modal('hide');
    this.reset();
});
