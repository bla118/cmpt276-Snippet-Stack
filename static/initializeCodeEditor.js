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