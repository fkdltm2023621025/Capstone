document.addEventListener('DOMContentLoaded', function() {
    function decodeWithSpacePreserved(queryString) {
        // Decode the entire query string
        const decoded = decodeURIComponent(queryString);
        // Replace all spaces with '%20' to preserve them
        return decoded.replace(/ /g, '%20');
    }

    const decodedSearch = decodeWithSpacePreserved(window.location.search);

    // 현재 페이지 URL을 서버로 전송
    fetch('/access_url', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            url: decodeURIComponent(window.location.pathname + decodedSearch),
            pathname : window.location.pathname, 
            search : decodedSearch
         })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error("Error:", data.error);
        } else {
            console.log("Success:", data.message);
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
});

