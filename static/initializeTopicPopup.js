// create-a-snippet editor
var codeEditor = new CodeMirror(document.getElementById("topic-content-box"), {
    mode: "python",
    autoRefresh: true,
    lineNumbers: true,
    theme: 'dracula'
});

codeEditor.refresh();

// changes the language mode of the code editor
document.getElementById("language-box").addEventListener('change', function() {
    codeEditor.setOption("mode", this.value);
});

// submission event handler for creating new snippet
document.getElementById("topic-form").addEventListener('submit', async function (event) {
    event.preventDefault();
    // get form values
    var formData = new FormData(document.getElementById("topic-form"));

    var contents = codeEditor.getValue();
    if (!contents) {
      alert("Snippet is empty! Cannot submit empty snippet!");
      return false;
    }

    // make a call to the backend to update database
    var pData = {};
    formData.forEach((value, key) => pData[key] = value);
    pData['code'] = contents;
    postData(pData);

    $('#startTopicModal').modal('hide');
    this.reset();
    codeEditor.setValue("");
})