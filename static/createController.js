async function postData(data) {
    const response = await fetch('http://127.0.0.1:5000/api/create_snippet',
                                {method: 'POST', body: JSON.stringify(data)});
    res = await response.json();
}

document.getElementById("submit_button").addEventListener('click', function() {
    let data = {};
    data['name'] = document.getElementById("snippet_name").value;
    data['language'] = document.getElementById("language").value;
    data['code'] = document.getElementById("code_input").value;
    postData(data);
    alert("Snippet created!");
});