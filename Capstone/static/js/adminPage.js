document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('.tab-button');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.style.display = 'none');

            this.classList.add('active');
            document.getElementById(this.dataset.tab).style.display = 'block';
        });
    });

    // 첫 번째 탭 기본 활성화
    tabs[0].classList.add('active');
    contents[0].style.display = 'block';

    // 버튼별 행 추가 및 토글 기능
    const managementButtons = document.querySelectorAll('.management-data');
    managementButtons.forEach(button => {
        button.addEventListener('click', function () {
            const currentRow = this.closest('tr'); // 현재 버튼이 속한 행
            let nextRow = currentRow.nextElementSibling;

            // 새 행이 이미 존재하고 있고, 토글을 위해 같은 버튼이 다시 눌렸는지 확인
            if (nextRow && nextRow.classList.contains('dynamic-row')) {
                nextRow.remove(); // 이미 생성된 행을 삭제하고 토글 종료
            } else {
                // 기존에 다른 버튼이 생성한 행이 있는 경우 삭제
                if (nextRow && nextRow.classList.contains('dynamic-row')) {
                    nextRow.remove();
                }

                // 새 행 생성
                nextRow = document.createElement('tr');
                nextRow.classList.add('dynamic-row'); // 동적 행에 스타일 적용을 위한 클래스 추가

                const cell = document.createElement('td');
                cell.colSpan = 8; // 새 행이 테이블 너비 전체를 차지하도록 설정

                // 버튼의 텍스트에 따라 다른 내용 표시
                switch (this.innerText) {
                    case '댓글':
                        const userId = currentRow.querySelector('td').textContent; // user_id 가져오기

                        // AJAX 요청으로 댓글 데이터 가져오기
                        fetch('/adminPage/get_comment', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ user_id: userId })
                        })
                            .then(response => response.json())
                            .then(data => {
                                // 댓글 데이터가 있는 경우와 없는 경우를 구분하여 표시
                                if (data.length > 0) {
                                    cell.innerHTML = `
                                        <div>
                                            <h4>댓글 내용</h4>
                                            <ul>
                                                ${data.map(comment => `<li>[${comment.name}] ${comment.comment}</li>`).join('')}
                                            </ul>
                                        </div>
                                    `;
                                } else {
                                    // 댓글이 없을 경우
                                    cell.innerHTML = `
                                        <div>
                                            <h4>댓글 내용</h4>
                                            <p>작성된 댓글 없음</p>
                                        </div>
                                    `;
                                }
                            })
                            .catch(error => {
                                console.error('Error fetching comments:', error);
                                cell.innerHTML = '댓글 데이터를 불러오는 중 오류가 발생했습니다.';
                            });
                        break;

                    case '닉네임 변경':
                        // 새 행에 닉네임 입력 폼 생성
                        cell.innerHTML = `
        <div>
            <label>변경할 닉네임:</label>
            <input type="text" id="new-nickname" placeholder="새 닉네임 입력">
            <button id="confirm-nickname-change">변경</button>
        </div>
    `;
                        nextRow.appendChild(cell);
                        currentRow.parentNode.insertBefore(nextRow, currentRow.nextSibling);

                        // 변경 버튼 클릭 이벤트 추가
                        document.getElementById('confirm-nickname-change').addEventListener('click', function () {
                            const userId = currentRow.querySelector('td').textContent; // user_id 가져오기
                            const newNickname = document.getElementById('new-nickname').value; // 입력 데이터 가져오기

                            // 입력 값이 비어있는지 확인
                            if (!newNickname) {
                                alert('새 닉네임을 입력해 주세요.');
                                return;
                            }

                            // AJAX 요청으로 닉네임 변경 요청
                            fetch('/adminPage/change_nickname', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({ user_id: userId, new_nickname: newNickname })
                            })
                                .then(response => response.json())
                                .then(data => {
                                    if (data.status === "success") {
                                        alert('닉네임이 변경되었습니다.');
                                        currentRow.querySelectorAll('td')[2].textContent = newNickname; // 화면에서 닉네임 업데이트
                                        nextRow.remove(); // 변경 완료 후 추가 행 삭제
                                    } else if (data.status === "failure") {
                                        alert('닉네임 변경에 실패했습니다.');
                                    }
                                })
                                .catch(error => {
                                    console.error('Error changing nickname:', error);
                                });
                        });
                        break;

                    // 탈퇴 기능 추가
                    case '탈퇴':
                        // 메세지와 YES 버튼 생성
                        cell.innerHTML = `
        <div>
            <p>정말 삭제하시겠습니까?</p>
            <button id="confirm-delete">YES</button>
        </div>
    `;
                        nextRow.appendChild(cell);
                        currentRow.parentNode.insertBefore(nextRow, currentRow.nextSibling);

                        // YES 버튼 클릭 이벤트 추가
                        document.getElementById('confirm-delete').addEventListener('click', function () {
                            const userId = currentRow.querySelector('td').textContent; // user_id 가져오기

                            // AJAX 요청으로 탈퇴 처리 요청
                            fetch('/adminPage/delete_user', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({ user_id: userId })
                            })
                                .then(response => response.json())
                                .then(data => {
                                    if (data.status === "success") {
                                        alert('회원이 삭제되었습니다.');
                                        currentRow.remove(); // 삭제된 행 제거
                                        nextRow.remove(); // 확인 행 제거
                                    } else if (data.status === "failure") {
                                        alert('회원 삭제에 실패했습니다.');
                                    }
                                })
                                .catch(error => {
                                    console.error('Error deleting user:', error);
                                });
                        });
                        break;

                }

                nextRow.appendChild(cell);
                currentRow.parentNode.insertBefore(nextRow, currentRow.nextSibling); // 현재 행 아래에 새 행 추가
            }
        });
    });
});
