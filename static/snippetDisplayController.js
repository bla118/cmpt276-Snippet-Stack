var currentSnippetIndex; // keeps track of the current snippet being edited
var snippetDisplay;
var snippets = [];
var allCode = document.getElementById("snippet-display").getElementsByClassName("snippet-body");

// initialize snippet display
Array.from(allCode).forEach((block) => {
  snippetDisplay = new CodeMirror(block, {
    mode: "javascript",
    lineNumbers: true,
    readOnly: "nocursor",
    theme: 'dracula'
  });
  // configure the displaays
  snippetDisplay.setValue("{{ snippet.code | tojson | safe }}");
  snippetDisplay.refresh();
  snippets.push(snippetDisplay);
})

// the editor for editing snippets
var snippetEditor = new CodeMirror(document.getElementById("editEditor"), {
  lineNumbers: true,
  autoRefresh: true,
  theme: 'dracula'
});
snippetEditor.refresh();

// deletes a snippet
function deleteSnippet() {
  if (confirm("Are you sure you want to delete this snippet?")) {
    var el = event.currentTarget.parentNode.parentNode;
    var i = Array.from(document.getElementById("snippet-display").getElementsByClassName("flex-snippet")).indexOf(el);

    // delete the code display for that snippet
    snippets.splice(i, 1);
    el.parentNode.removeChild(el);
    // make a call to the backend to update database
    //****************TODO*******************
  }
}

// copies the code inside the display to the editor
function editSnippet() {
    var snippetEl = event.currentTarget.parentNode.parentNode.previousElementSibling;
    // make a call to the backend to find out language of snippet
    //****************TODO*******************

    var language = "javascript"; // for testing
    snippetEditor.setOption("mode", language);

    // get the index of the snippet
    var i = Array.from(document.getElementById("snippet-display").getElementsByClassName("snippet-body")).indexOf(snippetEl);

    // copy value into snippet text editor
    snippetEditor.setValue(snippets[i].getValue());
    // save the index for form submission
    currentSnippetIndex = i;
}

// increment the likes count of the snippet
function addLike() {
  event.currentTarget.disabled = true;
  var snippetEl = event.currentTarget.parentNode.parentNode;
  var i = Array.from(document.getElementById("snippet-display").children).indexOf(snippetEl);

  var likesEl = event.currentTarget.firstChild;
  var likes = parseInt(likesEl.nodeValue, 10) + 1;
  likesEl.nodeValue = likes;
  // make a call to the backend to update database
  //****************TODO*******************
  
}

// calls backend for replies of snippet
// if no replies exist then alert the user (flash)
function getReplies() {
  var id = event.target.parentNode.parentNode.parentNode.id;

  // make a get call to the backend
  //****************TODO*******************

  // backend will redirect to active.html
}

// event handler for updating a snippet
document.getElementById("submitUpdatedSnippet").addEventListener('submit', function(event) {
    event.preventDefault(); // for testing

    // get the code from the editor
    // copy the code into the current snippet
    var contents = snippetEditor.getValue();
    if (!contents) {
      alert("Snippet is empty! Cannot submit empty snippet!");
      return false;
    }

    // make a call to the backend to update database
    //****************TODO*******************

    snippets[currentSnippetIndex].setValue(contents);
    $('#editModal').modal('hide');
});
