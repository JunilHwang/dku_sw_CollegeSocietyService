// static url 지정
var URL = "http://127.0.0.1:5000";

// board list component 정보
Vue.component('board-list',{
	template:getComponent("boardList"),
	data:function(){
		return {
			list:[]
		}
	},
	created:function(){
		var _this = this;
		$.get(URL+"/boardList",null,function(data){
			_this.list = JSON.parse(data);
		})
	},
	methods:{
		setView:function(data){
			console.log(data);
			bus.page = 'view';
			bus.getData = data
		}
	}
})

// board write component 지정
Vue.component('board-write',{
	template:getComponent("boardWrite"),
	methods:{
		insert:boardInsert
	}
})

// board update component 지정
Vue.component('board-update',{
	template:getComponent("boardUpdate"),
	methods:{
		update:boardUpdate
	}
})

// board view component 지정
Vue.component('board-view',{
	template:getComponent('boardView'),
	methods:{
		setList:function(){
			bus.page = 'list';
			bus.getData = null;
		},
		setDelete:function(){
			$.get(URL+"/boardDelete/"+bus.getData.idx,null,function(data){
				if(data == 'true'){
					alert('삭제되었습니다.')
					bus.page = 'list';
					bus.getData=null;
				}
			})
		},
		setUpdate:function(){
			bus.page = 'update';
		}
	}
})

// vue를 위한 data bus 생성
var bus = new Vue({
	data:{
		page:'list',
		getData:null,
	}
})

// app 시작
var app = new Vue({
	el: '#app'
})

$(document).on("click","a[href='#']",function(){ return false;})

// 게시물 추가
function boardInsert(event){
	event.preventDefault();
	var frm = event.target;
	$.ajax({
		type:'post',
		url:URL+"/boardInsert",
		data:$(frm).serialize(),
		success:function(data){
			data = JSON.parse(data);
			if(data.lastid){
				alert('추가되었습니다.')
				bus.page = 'list'
			}
		}
	})
}

// 게시물 업데이트
function boardUpdate(event){
	event.preventDefault();
	var frm = event.target;
	$.ajax({
		type:'post',
		url:URL+"/boardUpdate/"+bus.getData.idx,
		data:$(frm).serialize(),
		success:function(data){
			data = JSON.parse(data);
			if(data.idx){
				alert('수정되었습니다.')
				bus.page = 'view'
				bus.getData = data;
			}
		}
	})
}


// YYYY-mm-dd H:I:S 형태의 날짜 포맷 지정
function getDateFormat(dateValue){
	var date = new Date(dateValue);
	var
		y = date.getFullYear(),
		m = date.getMonth(),
		d = date.getDate(),
		h = date.getHours(),
		i = date.getMinutes(),
		s = date.getSeconds();
	if(m < 0) m = "0"+m;
	if(d < 0) d = "0"+d;
	if(h < 0) h = "0"+h;
	if(i < 0) i = "0"+i;
	if(s < 0) s = "0"+s;
	var dateFormat = y+'-'+m+'-'+d+' '+h+':'+i+':'+s;
	return ;
}

// ajax를 이용하여 component page를 불러온다.
function getComponent(page){
	var template = '';
	$.ajax({
		url:'/static/component/'+page+'.html',
		type:'get',
		async:false,
	}).done(function(data){
		template = data;
	})
	return template;
}