// 이미지 선택시 DB 테이블 선택
function updatedataSelect(valueToSend) {
    fetch("/update_data_select", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({value: valueToSend})
    })
    .then(response => {
        if (response.ok) {
            // 성공적으로 업데이트된 경우 index 페이지로 이동
            window.location.href = '/index';
        } else {
            // 실패한 경우 사용자에게 메시지 표시
            alert('Failed to update data selection.');
            console.error('Failed to update data_select');
        }
    })
    .catch(error => {
        alert('Error updating data selection. Please try again.');
        console.error('Error updating data_select:', error);
    });
}

document.getElementById("clickable-image").addEventListener("click", function() {
    updatedataSelect("0");
});

document.getElementById("clickable-image_2").addEventListener("click", function() {
    updatedataSelect("1");
});
