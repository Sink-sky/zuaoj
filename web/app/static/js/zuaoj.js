function encode_params(params)
{
    params = params.replace(/%/g, "%25");
	params = params.replace(/\&/g, "%26");
	params = params.replace(/\+/g, "%2B");
    return params;
}

function getDate(){
    var date = new Date();

    var year = date.getFullYear(),
        month = date.getMonth() + 1,
        day = date.getDate(),
        hour = date.getHours(),
        min = date.getMinutes(),
        sec = date.getSeconds();
    var newTime = year + '/' +
                month + '/' +
                day + ' ' +
                hour + ':' +
                min + ':' +
                sec;
    return newTime;
}

function submit(problem_id)
{
    var xmlHttp = new XMLHttpRequest();
	var url = "/submit/";
    
	var source_code = editor.getValue();
	source_code = source_code.replace(/%/g, "%25");
	source_code = source_code.replace(/\&/g, "%26");
	source_code = source_code.replace(/\+/g, "%2B");
    
    var language = document.getElementById('language').getAttribute('value');
    var params = "problem_id=" + problem_id.toString() + "&source_code=" + source_code + "&language=" + language;

	xmlHttp.onreadystatechange = function(){
		if(xmlHttp.readyState == 4 && xmlHttp.status == 200){
			var submit_id = xmlHttp.responseText;
            
            document.getElementById('refresh').onclick = function(){get_result(submit_id); };
            
            get_result(submit_id);
		}
		else if(xmlHttp.readyState == 4 && xmlHttp.status == 400)
		{
			var result_td = document.getElementById('result');
			
			result_td.innerHTML = '未提交';
			result_td.className = 'text-danger';
			
			alert('比赛已结束');
		}
	}
	xmlHttp.open("POST", url, true);
	xmlHttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	xmlHttp.send(params);
	
	var result_td = document.getElementById('result');
	var result_table = document.getElementById('result_table');
	var compile_info_div = document.getElementById('compile_information');
	
	result_td.innerHTML = '评测中';
	result_td.className = 'text-success';
    result_td.parentNode.children[0].innerHTML = getDate();
    result_td.parentNode.children[3].innerHTML = problem_id;
    result_td.parentNode.children[4].innerHTML = document.getElementById('language').childNodes[0].data;
	
	result_table.className = 'table hidden';
	result_table.removeChild(result_table.children[1]);
	var tbody_node = document.createElement('tbody');
	result_table.appendChild(tbody_node);
	
	compile_info_div.className = 'hidden';
	compile_info_div.children[1].innerHTML = '';
	
}

function get_result(submit_id, is_history_query=false)
{
    var OJ_AC = '0';
    var OJ_WA = '1';
    var OJ_PE = '2';
    var OJ_TL = '3';
    var OJ_ML = '4';
    var OJ_CE = '5';
    var OJ_WT = '6';
    
    var url = "/result/";
	var params = "submit_id=" + submit_id;
    
    var xmlHttp = new XMLHttpRequest();
	
	show_editor.setValue("");
    
	xmlHttp.onreadystatechange = function(){
		if(xmlHttp.readyState == 4 && xmlHttp.status == 200){
            var result = JSON.parse(xmlHttp.responseText);
			
			show_editor.setValue(result['source_code'] + "\n");
			show_editor.moveCursorTo(0, 0);
			
			if(is_history_query)
			{
				var result_td = document.getElementById('result');
				var result_table = document.getElementById('result_table');
				var compile_info_div = document.getElementById('compile_information');
				var source_code_div = document.getElementById('source_code');
				
				result_td.innerHTML = '';
				result_td.className = 'text-success';
				result_td.parentNode.children[0].innerHTML = result['time'];
				result_td.parentNode.children[3].innerHTML = result['problem_id'];
				
				var lan;
				if(result['language'] == 0)
					lan = 'C (gcc)';
				else if(result['language'] == 1)
					lan = 'C++ (g++)';
				else if(result['language'] == 2)
					lan = 'Java (jdk)';
				else if(result['language'] == 3)
					lan = 'Python (python 3)'
				result_td.parentNode.children[4].innerHTML = lan;
	
				result_table.className = 'table hidden';
				result_table.removeChild(result_table.children[1]);
				var tbody_node = document.createElement('tbody');
				result_table.appendChild(tbody_node);
	
				compile_info_div.className = 'hidden';
				compile_info_div.children[1].innerHTML = '';
			}
            
            if(result['result_status'][0] == OJ_CE){
                document.getElementById('result').innerHTML = "编译错误";
                document.getElementById('result').className = "text-primary";
                
                var compile_information = document.getElementById('compile_information');
                
                if(compile_information.className.substr(compile_information.className.length - 6, 6) == "hidden"){
                    compile_information.className = compile_information.className.substr(0, compile_information.className.length - 6);
                    
                    compile_information.children[1].innerHTML = result['compile_info']
                }
            }else{
                var result_table = document.getElementById('result_table');
                
                var result_ls = result['result_status'].split(';')[0].split(',');
                var time_ls = result['result_status'].split(';')[1].split(',');
				
				document.getElementById('result').parentNode.children[2].innerHTML = result['total_score'];
                
                
                if(result_table.className.substr(result_table.className.length - 6, 6) == "hidden"){
                    result_table.className = result_table.className.substr(0, result_table.className.length - 6);
                    
                    var is_ac = 1;
                    var is_wa = 1;
                    for(var i = 0; i < result_ls.length; i++){
                        
                        var tr = document.createElement('tr');
                        
                        var td_ls = new Array();
                        for(var j = 0; j < 4; j++)
                            td_ls[j] = document.createElement('td');
                        
                        if(result_ls[i] == OJ_AC){
                            is_wa = 0;
                            td_ls[1].className = "text-success";
                            var td1_text = document.createTextNode("Accepted");
                        }else if(result_ls[i] == OJ_WA){
                            is_ac = 0;
                            td_ls[1].className = "text-danger";
                            var td1_text = document.createTextNode("Woring Answer");
                        }else if(result_ls[i] == OJ_PE){
                            is_ac = 0;
                            td_ls[1].className = "text-danger";
                            var td1_text = document.createTextNode("Runtime Error");
                        }else if(result_ls[i] == OJ_TL){
                            is_ac = 0;
                            td_ls[1].className = "text-danger";
                            var td1_text = document.createTextNode("Time Limit Exceeded");
                        }else if(result_ls[i] == OJ_AC){
                            is_ac = 0;
                            td_ls[1].className = "text-danger";
                            var td1_text = document.createTextNode("Memory Limit Exceeded");
                        }
                        
                        var td2_text = document.createTextNode(time_ls[i] + " ms");
                        
                        td_ls[0].appendChild(document.createTextNode(i));
                        td_ls[1].appendChild(td1_text);
                        td_ls[2].appendChild(td2_text);
                        
                        for(var j = 0; j < 4; j++)
                            tr.appendChild(td_ls[j]);
                        result_table.children[1].appendChild(tr);
                    }
                    if(is_ac && !is_wa){
						document.getElementById('result').innerHTML = "全部正确";
                        document.getElementById('result').className = "text-success";
					}else if(!is_ac && !is_wa){
						document.getElementById('result').innerHTML = "部分正确";
                        document.getElementById('result').className = "text-danger";
                    }else{
						document.getElementById('result').innerHTML = "全部错误";
                        document.getElementById('result').className = "text-danger";
                    }
                }
            }
        }
	}
    
	xmlHttp.open("GET", url+'?'+params, true);
	xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xmlHttp.send(null);
}

function get_result_history_query(submit_id)
{	
	get_result(submit_id, true);
}

function get_last_submit(problem_id)
{
	var url = "/last-submit";
	var params = "problem_id=" + problem_id;
	var xmlHttp = new XMLHttpRequest();
	
	xmlHttp.onreadystatechange = function(){
		if(xmlHttp.readyState == 4 && xmlHttp.status == 200){
			var last_submit = JSON.parse(xmlHttp.responseText);
			editor.setValue(last_submit['source_code']);
			editor.moveCursorTo(0, 0);
		}
	}
	xmlHttp.open("GET", url+'?'+params, true);
	xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xmlHttp.send(null);
}

function switch_language(obj)
{
	document.getElementById('language').innerHTML = obj.innerHTML;
	document.getElementById('language').setAttribute('value', obj.getAttribute('value'));
	
}

function request_delete(url, key, value)
{
    var xmlHttp = new XMLHttpRequest();
    var params = key + '=' + value;
    
    xmlHttp.onreadystatechange = function(){
		if(xmlHttp.readyState == 4 && xmlHttp.status == 200){
            location.reload();
        }
    }
    
    xmlHttp.open("DELETE", url, true);
    xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xmlHttp.send(params);
}

function bind_student_id()
{
	var xmlHttp = new XMLHttpRequest();
	var student_id_input = document.getElementById("student_id_input");
	var url = "/user/information/bind-student-id/";
	var params = "student_id=" + student_id_input.value;
	
	xmlHttp.onreadystatechange = function(){
		if(xmlHttp.readyState == 4 && xmlHttp.status == 200){
            location.reload();
        }else if(xmlHttp.readyState == 4 && xmlHttp.status == 400){
			alert("绑定失败");
		}
    }
    
    xmlHttp.open("POST", url, true);
    xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xmlHttp.send(params);
}

function get_news(news_id)
{
	var xmlHttp = new XMLHttpRequest();
	var url = '/manager/news/?news_id=' + news_id;
    
    xmlHttp.onreadystatechange = function(){
		if(xmlHttp.readyState == 4 && xmlHttp.status == 200){
            var news = JSON.parse(xmlHttp.responseText);
			var news_dialog_node = document.getElementById('edit_modalDialog_body');
			
			news_dialog_node.children[0].children[0].children[1].value = news['title'];
			news_dialog_node.children[0].children[1].children[1].value = news['content'];
			
			news_dialog_node.children[1].children[0].onclick = function(){update_news(news_id); }; 
        }
    }
    
    xmlHttp.open("GET", url, true);
    xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xmlHttp.send();
}

function update_news(news_id)
{
	var xmlHttp = new XMLHttpRequest();
	var url = '/manager/news/?news_id=' + news_id;
	var params = '';
	
	var group_dialog_node = document.getElementById('edit_modalDialog_body');
			
	params += 'title=' + group_dialog_node.children[0].children[0].children[1].value;
	params += '&content=' + group_dialog_node.children[0].children[1].children[1].value
    
    xmlHttp.onreadystatechange = function(){
		if(xmlHttp.readyState == 4 && xmlHttp.status == 200){
            location.reload();
        }
    }
    
    xmlHttp.open("PUT", url, true);
    xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xmlHttp.send(params);
}

function get_group(group_id)
{
	var xmlHttp = new XMLHttpRequest();
	var url = '/manager/group/?group_id=' + group_id;
    
    xmlHttp.onreadystatechange = function(){
		if(xmlHttp.readyState == 4 && xmlHttp.status == 200){
            var group = JSON.parse(xmlHttp.responseText);
			var group_dialog_node = document.getElementById('edit_modalDialog_body');
			
			group_dialog_node.children[0].children[0].children[1].value = group['group_name'];
			group_dialog_node.children[0].children[1].children[1].value = group['user_ls'];
			group_dialog_node.children[0].children[2].children[1].value = group['student_id_ls'];
			
			group_dialog_node.children[1].children[0].onclick = function(){update_group(group_id); }; 
        }
    }
    
    xmlHttp.open("GET", url, true);
    xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xmlHttp.send();
}

function update_group(group_id)
{
	var xmlHttp = new XMLHttpRequest();
	var url = '/manager/group/?group_id=' + group_id;
	var params = '';
	
	var group_dialog_node = document.getElementById('edit_modalDialog_body');
			
	params += 'group_name=' + group_dialog_node.children[0].children[0].children[1].value;
	params += '&user_ls=' + group_dialog_node.children[0].children[1].children[1].value
	params += '&student_id_ls=' + group_dialog_node.children[0].children[2].children[1].value
    
    xmlHttp.onreadystatechange = function(){
		if(xmlHttp.readyState == 4 && xmlHttp.status == 200){
            location.reload();
        }
    }
    
    xmlHttp.open("PUT", url, true);
    xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xmlHttp.send(params);
}

function get_problem(problem_id)
{
	var xmlHttp = new XMLHttpRequest();
	var url = '/manager/problem/?problem_id=' + problem_id;
    
    xmlHttp.onreadystatechange = function(){
		if(xmlHttp.readyState == 4 && xmlHttp.status == 200){
            var problem = JSON.parse(xmlHttp.responseText);
			var problem_dialog_node = document.getElementById('edit_modalDialog_body');
			
			problem_dialog_node.children[0].children[0].children[1].value = problem['problem_id'];
			problem_dialog_node.children[0].children[1].children[1].value = problem['title'];
			problem_dialog_node.children[0].children[2].children[1].value = problem['description'];
			problem_dialog_node.children[0].children[3].children[2].value = problem['time_limit'];
			problem_dialog_node.children[0].children[4].children[2].value = problem['memory_limit'];
			problem_dialog_node.children[0].children[5].children[1].value = problem['input_specification'];
			problem_dialog_node.children[0].children[6].children[1].value = problem['output_specification'];
			problem_dialog_node.children[0].children[7].children[1].value = problem['sample_input'];
			problem_dialog_node.children[0].children[8].children[1].value = problem['sample_output'];
			problem_dialog_node.children[0].children[9].children[1].value = problem['test_input'];
			problem_dialog_node.children[0].children[10].children[1].value = problem['test_output'];
			problem_dialog_node.children[0].children[11].children[1].value = problem['test_point_score'];
			problem_dialog_node.children[0].children[12].children[1].value = problem['problem_status'];
			 
			problem_dialog_node.children[1].children[0].onclick = function(){update_problem(problem_id); }; 
        }
    }
    
    xmlHttp.open("GET", url, true);
    xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xmlHttp.send();
}

function update_problem(problem_id)
{
	var xmlHttp = new XMLHttpRequest();
	var url = '/manager/problem/?problem_id=' + problem_id;
	var params = '';
	
	var problem_dialog_node = document.getElementById('edit_modalDialog_body');
			
	params += 'problem_id=' + problem_dialog_node.children[0].children[0].children[1].value;
	params += '&title=' + problem_dialog_node.children[0].children[1].children[1].value;
	params += '&description=' + problem_dialog_node.children[0].children[2].children[1].value;
	params += '&time_limit=' + problem_dialog_node.children[0].children[3].children[2].value;
	params += '&memory_limit=' + problem_dialog_node.children[0].children[4].children[2].value;
	params += '&input_specification=' + problem_dialog_node.children[0].children[5].children[1].value;
	params += '&output_specification=' + problem_dialog_node.children[0].children[6].children[1].value;
	params += '&sample_input=' + problem_dialog_node.children[0].children[7].children[1].value;
	params += '&sample_output=' + problem_dialog_node.children[0].children[8].children[1].value;
	params += '&test_input=' + problem_dialog_node.children[0].children[9].children[1].value;
	params += '&test_output=' + problem_dialog_node.children[0].children[10].children[1].value;
	params += '&test_point_score=' + problem_dialog_node.children[0].children[11].children[1].value;
	params += '&problem_status=' + problem_dialog_node.children[0].children[12].children[1].value;
    
    xmlHttp.onreadystatechange = function(){
		if(xmlHttp.readyState == 4 && xmlHttp.status == 200){
            location.reload();
        }
    }
    
    xmlHttp.open("PUT", url, true);
    xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xmlHttp.send(params);
}

function get_competition(competition_id)
{
	var xmlHttp = new XMLHttpRequest();
	var url = '/manager/competition/?competition_id=' + competition_id;
    
    xmlHttp.onreadystatechange = function(){
		if(xmlHttp.readyState == 4 && xmlHttp.status == 200){
            var competition = JSON.parse(xmlHttp.responseText);
			var competition_dialog_node = document.getElementById('edit_modalDialog_body');
			
			competition['begin_date'] = new Date(competition['begin_date']);
			competition['end_date'] = new Date(competition['end_date']);
			
			competition_dialog_node.children[0].children[0].children[1].value = competition['title'];
			competition_dialog_node.children[0].children[1].children[1].value = competition['begin_date'].getUTCFullYear();
			competition_dialog_node.children[0].children[1].children[2].value = competition['begin_date'].getUTCMonth() + 1;
			competition_dialog_node.children[0].children[1].children[3].value = competition['begin_date'].getUTCDate();
			competition_dialog_node.children[0].children[1].children[4].value = competition['begin_date'].getUTCHours();
			competition_dialog_node.children[0].children[1].children[6].value = competition['begin_date'].getUTCMinutes();
			competition_dialog_node.children[0].children[2].children[1].value = competition['end_date'].getUTCFullYear();
			competition_dialog_node.children[0].children[2].children[2].value = competition['end_date'].getUTCMonth() + 1;
			competition_dialog_node.children[0].children[2].children[3].value = competition['end_date'].getUTCDate();
			competition_dialog_node.children[0].children[2].children[4].value = competition['end_date'].getUTCHours();
			competition_dialog_node.children[0].children[2].children[6].value = competition['end_date'].getUTCMinutes();
			competition_dialog_node.children[0].children[3].children[1].value = competition['problem_ls'];
			competition_dialog_node.children[0].children[4].children[1].value = competition['group_id'];
			
			competition_dialog_node.children[1].children[0].onclick = function(){update_competition(competition_id); }; 
        }
    }
    
    xmlHttp.open("GET", url, true);
    xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xmlHttp.send();
}

function update_competition(competition_id)
{
	var xmlHttp = new XMLHttpRequest();
	var url = '/manager/competition/?competition_id=' + competition_id;
	var params = '';
	
	var competition_dialog_node = document.getElementById('edit_modalDialog_body');
			
	params += 'title=' + competition_dialog_node.children[0].children[0].children[1].value;
	params += '&begin_date_year=' + competition_dialog_node.children[0].children[1].children[1].value;
	params += '&begin_date_month=' + competition_dialog_node.children[0].children[1].children[2].value;
	params += '&begin_date_day=' + competition_dialog_node.children[0].children[1].children[3].value;
	params += '&begin_date_hour=' + competition_dialog_node.children[0].children[1].children[4].value;
	params += '&begin_date_min=' + competition_dialog_node.children[0].children[1].children[6].value;
	params += '&end_date_year=' + competition_dialog_node.children[0].children[2].children[1].value;
	params += '&end_date_month=' + competition_dialog_node.children[0].children[2].children[2].value;
	params += '&end_date_day=' + competition_dialog_node.children[0].children[2].children[3].value;
	params += '&end_date_hour=' + competition_dialog_node.children[0].children[2].children[4].value;
	params += '&end_date_min=' + competition_dialog_node.children[0].children[2].children[6].value;
	params += '&problem_ls=' + competition_dialog_node.children[0].children[3].children[1].value;
	params += '&group_id=' + competition_dialog_node.children[0].children[4].children[1].value;
    
    xmlHttp.onreadystatechange = function(){
		if(xmlHttp.readyState == 4 && xmlHttp.status == 200){
            location.reload();
        }
    }
    
    xmlHttp.open("PUT", url, true);
    xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xmlHttp.send(params);
}