document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData();
    const zipFile = document.getElementById('zipFile').files[0];
    formData.append('zipFile', zipFile);

    fetch('/convert', {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (!response.ok) {
            console.log("Network response was not ok");
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log(data); // Log the response data
        if(data && data.success) {
            const outputTableDiv = document.getElementById('outputTable');
            outputTableDiv.innerHTML = data.table_content;
        } else if (data && data.error) {
            alert('Error: ' + data.error);
        } else {
            alert('Unknown error occurred');
        }
    })
    .catch(error => {
        console.log('Error:', error);
        alert('An error occurred while processing your file.');
    });
});
