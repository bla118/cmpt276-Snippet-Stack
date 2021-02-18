// let urlForDelete = "http://127.0.0.1:5000/api/delete_snippet";
// let urlForSearch = "http://127.0.0.1:5000/api/fetch_snippet";
let urlForDelete = "https://snippet-stack.herokuapp.com/api/delete_snippet";
let urlForSearch = "https://snippet-stack.herokuapp.com/api/fetch_snippet";

async function deleteEntry(data)
{
    const response = await fetch(urlForDelete,
                                {method: 'POST', body: JSON.stringify(data)});
    let res = await response.json();
    console.log("deleted " + data['idToDel']);
    return res;
}

async function getData(data) 
{
    const response = await fetch(urlForSearch,
                                {method: 'POST', body: JSON.stringify(data)});
    res = await response.json();
    let resultList = document.getElementById("search-results");
    resultList.innerHTML = "";

    for (searchRes of res)
    {
        let idToDel = searchRes[0];
        console.log(idToDel);
        console.log(typeof idToDel)
        let name = searchRes[1];
        let lang = searchRes[2];
        let code = searchRes[3];

        let gap = document.createElement('p');
        let delButton = document.createElement('button');
        delButton.innerText = 'X';
        delButton.addEventListener('click', function() {
            let data = {};
            data['idToDel'] = idToDel;
            deleteEntry(data);
            alert("Snippet deleted!");
        });

        let label = document.createElement('label');
        label.innerText = `  ${lang} - ${name}`;
        resultList.appendChild(delButton);
        resultList.appendChild(label);

        let codeBlock = document.createElement('pre');
        let content = document.createElement('code');
        content.className = lang;
        content.innerText = code;
        codeBlock.appendChild(content);

        resultList.appendChild(codeBlock);
    }

    document.querySelectorAll('pre code').forEach((block) => hljs.highlightBlock(block));
    return res;
}


document.getElementById("submit_button").addEventListener("click", function() {
    let data = {};
    data['language'] = document.getElementById("language_field").value;
    data['search_key'] = document.getElementById("search_term").value;
    getData(data);
});