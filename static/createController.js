// let urlForCreate = 'http://127.0.0.1:5000/api/create_snippet';
let urlForCreate = "https://snippet-stack.herokuapp.com/api/create_snippet";

async function postData(data) {
    const response = await fetch(urlForCreate,
                                {method: 'POST', body: JSON.stringify(data)});
    res = await response.json();
}