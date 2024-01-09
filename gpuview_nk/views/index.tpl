<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">
    <title>gpuview</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" 
        integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous"/>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css" 
        rel="stylesheet" type="text/css"/>
    <link href="https://cdn.datatables.net/1.10.16/css/dataTables.bootstrap4.min.css" rel="stylesheet"/>
</head>

<body class="fixed-nav sticky-footer bg-dark" id="page-top">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top" id="mainNav">
        <a class="navbar-brand" href="/"><h2>[gpuview dashboard]</h2></a>
        <button class="navbar-toggler navbar-toggler-right" type="button" data-toggle="collapse" 
            data-target="#navbarResponsive"
            aria-controls="navbarResponsive" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarResponsive">
            <ul class="navbar-nav navbar-sidenav" id="exampleAccordion">
                <li class="nav-item" data-toggle="tooltip" data-placement="right" title="Table">
                    <!-- a class="nav-link" href="#table">
                        <i class="fas fa-table"></i>
                        <span class="nav-link-text">Table</span>
                    </a -->
                </li>
            </ul>
        </div>
    </nav>
    <div class="content-wrapper">
        <div class="container-fluid" style="padding: 70px 40px 40px 40px">
            <div class="row">
                % for gpustat in gpustats:
                <div class="col-12 mb-3">
                    <div style="display: flex; align-items: center;">
                        <!-- Hostname -->
                        <h4 style="margin-right: 20px; color: white;">{{ gpustat.get('hostname', '-') }}</h4>

                        <!-- Dropdown and Use button -->
                        <select id="userDropdown-{{ gpustat.get('hostname', '-') }}" class="dropdown" style="width: 70px; height: 30px; margin-right: 10px; font-size: 16px;">
                            <option value="사용자">사용자</option>
                            <option value="김희원">김희원</option>
                            <option value="배상우">배상우</option>
                            <option value="이강규">이강규</option>
                            <option value="박혁인">박혁인</option>
                            <option value="김수현">김수현</option>
                            <option value="민소연">민소연</option>
                            <option value="이남경">이남경</option>
                        </select>

                        <!-- Date range selection -->
                        <input type="date" id="endDate-{{ gpustat.get('hostname', '-') }}" class="endDate" style="margin-right: 10px;">

                        <button onclick="applyUser('{{ gpustat.get('hostname', '-') }}')" style="padding: 3px 6px; border-radius: 5px; cursor: pointer; margin-right: 35px;">사용예정</button>

                        <!-- User list with horizontal layout -->
                        <div id="userList-{{ gpustat.get('hostname', '-') }}" style="display: flex; color: white;">
                            <!-- Dynamically filled with users -->
                            % user_info = gpustat.get('user_info', {})
                            % if user_info:
                                % for user, date in user_info.items():
                                    {{ user }}: {{ date }}
                                    <button onclick="removeUser('{{ gpustat.get('hostname', '-') }}', '{{ user }}')" style="border-radius: 50%; width: 25px; height: 25px; line-height: 10px; text-align: center; border: 1px solid #000; font-size: 20px; margin-right: 20px; margin-left: 5px;">x</button>

                                % end
                            % else:
                                -
                            % end
                        </div>

                    </div>
                </div>
                % for gpu in gpustat.get('gpus', []):
                <div class="col-xl-3 col-md-4 col-sm-6 mb-3">
                    <div class="card text-white {{ gpu.get('flag', '') }} o-hidden h-100">
                        <div class="card-body">
                            <div class="float-left">
                                <div class="card-body-icon">
                                    <i class="fa fa-server"></i> <b>{{ gpustat.get('hostname', '-') }}</b>
                                </div>
                                <div>[{{ gpu.get('index', '') }}] {{ gpu.get('name', '-') }}</div>
                            </div>
                        </div>
                        <div class="card-footer text-white clearfix small z-1">
                            <span class="float-left">
                                <span class="text-nowrap">
                                <i class="fa fa-thermometer-three-quarters" aria-hidden="true"></i>
                                Temp. {{ gpu.get('temperature.gpu', '-') }}&#8451; 
                                </span> |
                                <span class="text-nowrap">
                                <i class="fa fa-microchip" aria-hidden="true"></i>
                                Mem. {{ gpu.get('memory', '-') }}% 
                                </span> |
                                <span class="text-nowrap">
                                <i class="fa fa-cogs" aria-hidden="true"></i>
                                Util. {{ gpu.get('utilization.gpu', '-') }}%
                                </span> |
                                <span class="text-nowrap">
                                <i class="fa fa-users" aria-hidden="true"></i>
                                {{ gpu.get('users', '-') }}
                                </span>
                            </span>
                        </div>
                    </div>
                </div>
                % end
                % end
            </div>
            <!-- GPU Stat Card-->
            <div class="card mb-3">
                <div class="card-header">
                    <i class="fa fa-table"></i> All Hosts and GPUs</div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-bordered" id="dataTable" width="100%" cellspacing="0">
                            <thead>
                                <tr>
                                    <th scope="col">Host</th>
                                    <th scope="col">GPU</th>
                                    <th scope="col">Temp.</th>
                                    <th scope="col">Util.</th>
                                    <th scope="col">Memory Use/Cap</th>
                                    <th scope="col">Power Use/Cap</th>
                                    <th scope="col">User Processes</th>
                                </tr>
                            </thead>
                            <tbody>
                                % for gpustat in gpustats:
                                % for gpu in gpustat.get('gpus', []):
                                <tr class="small" id={{ gpustat.get('hostname', '-') }}>
                                    <th scope="row">{{ gpustat.get('hostname', '-') }} </th>
                                    <td> [{{ gpu.get('index', '') }}] {{ gpu.get('name', '-') }} </td>
                                    <td> {{ gpu.get('temperature.gpu', '-') }}&#8451; </td>
                                    <td> {{ gpu.get('utilization.gpu', '-') }}% </td>
                                    <td> {{ gpu.get('memory', '-') }}% ({{ gpu.get('memory.used', '') }}/{{ gpu.get('memory.total', '-') }}) </td>
                                    <td> {{ gpu.get('power.draw', '-') }} / {{ gpu.get('enforced.power.limit', '-') }} </td>
                                    <td> {{ gpu.get('user_processes', '-') }} </td>
                                </tr>
                                % end
                                % end
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="card-footer small text-muted">{{ update_time }}</div>
            </div>
            <footer class="sticky-footer">
                <div class="container">
                    <div class="text-center text-white">
                        <small><a href='https://github.com/fgaim/gpuview'>gpuview</a> © 2018</small>
                    </div>
                </div>
            </footer>
        </div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                var endDateInputs = document.getElementsByClassName('endDate');
                var today = new Date().toISOString().split('T')[0];

                Array.prototype.forEach.call(endDateInputs, function(input) {
                    input.setAttribute('min', today);
                });
            });

            function applyUser(hostname) {
                var user = document.getElementById('userDropdown-' + hostname).value;
                var endDate = document.getElementById('endDate-' + hostname).value;
                
                // 데이터 검증
                if (user === "사용자") {
                    alert("사용자를 선택해주세요.");
                    return;
                }
                if (!endDate) {
                    alert("종료 날짜를 선택해주세요.");
                    return;
                }

                var confirmSubmission = confirm(user + "님, " + hostname + "를 " + endDate + "까지 사용하시겠습니까?");
                if (!confirmSubmission) {
                    return; // 사용자가 취소를 눌렀을 경우 함수 실행 중지
                }

                // Send data to your Flask route
                var xhttp = new XMLHttpRequest();
                xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                        var response = JSON.parse(this.responseText);
                        console.log(response.gpu_users);
                        updateUserInfo(response.gpu_users);
                    }
                };
                // URL 인코딩된 쿼리 문자열 생성
                var queryString = "user=" + encodeURIComponent(user) +
                                "&hostname=" + encodeURIComponent(hostname) +
                                "&endDate=" + encodeURIComponent(endDate);

                xhttp.open("GET", "/apply_user?" + queryString, true);
                xhttp.send();
            }
            function updateUserInfo(gpuUsers) {
                for (var hostname in gpuUsers) {
                    if (gpuUsers.hasOwnProperty(hostname)) {
                        var userDict = gpuUsers[hostname];
                        var userListElement = document.getElementById('userList-' + hostname);

                        // 사용자 목록을 문자열로 변환
                        var userListHtml = '';
                        for (var userName in userDict) {
                            if (userDict.hasOwnProperty(userName)) {
                                userListHtml += '<span>' + userName + ': ' + userDict[userName] + '</span> <button onclick="removeUser(\'' + hostname + '\', \'' + userName + '\')" style="border-radius: 50%; width: 25px; height: 25px; line-height: 10px; text-align: center; border: 1px solid #000; font-size: 20px; margin-right: 20px; margin-left: 5px;">x</button>';

                            }
                        }
                        // 마지막 쉼표와 공백 제거
                        userListHtml = userListHtml.replace(/, $/, '');

                        // 사용자 정보 업데이트
                        if (userListElement) {
                            userListElement.innerHTML = userListHtml || '-';
                        }
                    }
                }
            }
            function removeUser(hostname, user) {
                // AJAX 요청을 사용하여 서버에 사용자 삭제 요청을 보냅니다.
                // 예시: 여기서는 간단히 서버의 삭제 API를 호출하는 코드를 작성합니다.
                var confirmSubmission = confirm(user + "님, " + hostname + "서버 사용을 취소하시겠습니까?");
                if (!confirmSubmission) {
                    return; // 사용자가 취소를 눌렀을 경우 함수 실행 중지
                }
                var xhttp = new XMLHttpRequest();
                xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                        var response = JSON.parse(this.responseText);
                        console.log(response.gpu_users);
                        updateUserInfo(response.gpu_users);
                    }
                };
                xhttp.open("GET", "/remove_user?hostname=" + encodeURIComponent(hostname) + "&user=" + encodeURIComponent(user), true);
                xhttp.send();
            }

        </script>
        <script src="https://code.jquery.com/jquery-3.3.1.min.js" 
            integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8="
            crossorigin="anonymous"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" 
            integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl"
            crossorigin="anonymous"></script>
        <script src="https://cdn.datatables.net/1.10.16/js/jquery.dataTables.min.js"></script>
        <script src="https://cdn.datatables.net/1.10.16/js/dataTables.bootstrap4.min.js"></script>
    </div>
</body>

</html>
