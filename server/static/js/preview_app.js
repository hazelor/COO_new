/**
 * Created by guoxiao on 16/2/27.
 */
var sign;
function on_selected_device_change(){
    var sel_device_id = document.getElementById("sel_device").value;
    $.ajax({
        url:'/data/preview',
        type:'post',
        data:{'dev_id': sel_device_id},
        success:function(data, status){
            chamber_list = JSON.parse(data)
            $("#sel_chamber option").remove();
            for(i=0;i<chamber_list.length;i++){
                //alert("<option value="+"'"+data_list[i][0]+"'"+">"+data_list[i][1]+"</option>")
                $("#sel_chamber").append("<option value="+chamber_list[i]+">"+chamber_list[i]+"</option>");
            }

        }
    })
}
function on_selected_change(){
    //render_chart([[],[]])
    var date = new Date()
    var end_time = date.pattern("yyyy-MM-dd hh:mm");
    var date_milliseconds = date.getTime();
    date_milliseconds -= 1000*60*59;
    date = new Date(date_milliseconds);
    var start_time = date.pattern("yyyy-MM-dd hh:mm");
    //var chart = $('#container').highcharts()
    //var series = chart.series;
    //series[0].remove(false)
    //series[1].remove(false)
    if(sign){
        clearInterval(sign)
    }

    var chart_content_info = get_chart_content_info($('#sel_chamber').children('option:selected').attr('value'));
    var inner_HTML_str = "";
    for(var i =0;i<chart_content_info.length;i++)
    {

        inner_HTML_str=inner_HTML_str + "<div id='"+ chart_content_info[i]['container_id']+"'></div>"

    }
    document.getElementById("charts").innerHTML = inner_HTML_str;

    if ($('#sel_chamber').children('option:selected').val() != ''){
        //var title = {
        //    text:$('#chamber_name').children('option:selected').text()
        //}
        //var chart = new Highcharts.Chart()
        //chart.setTitle(title)

        loading_begin('数据准备中')
        //alert('--------test--------')
        $.ajax({
                url:'history/query',
                type:'GET',
                timeout: 20000,
                dataType:'text',
                data:{'dev_id':$('#sel_device').children('option:selected').attr('value'),
                      'owner':$('#sel_chamber').children('option:selected').attr('value'),
                      'start_time':start_time,
                      'end_time':end_time
                      },
                success:function(data, status){
                    if(data==''){
                        //alert('所选择的时间段没有数据!')
                        loading_end();
                    }
                    else{
                        var jdata= $.parseJSON(data);
                        var chart_content_info = get_chart_content_info($('#sel_chamber').children('option:selected').attr('value'));
                        for(var i=0;i<chart_content_info.length;i++){
                            var datas = new Array();
                            for(var j = 0; j<chart_content_info[i]['data_type_ids'].length;j++){
                                var data = {'name':'','data':[]};
                                var jd = get_data_by_type_id(jdata, chart_content_info[i]['data_type_ids'][j]);
                                data['name'] = jd['name'];
                                data['data'] = jd['values'];
                                datas.push(data)
                            }
                            render_chart(datas,chart_content_info[i]['title'],chart_content_info[i]['unit'],chart_content_info[i]['container_id']);
                        }
                    }
                        loading_end()
                    },
                error:function(jqXHR, textStatus, errorThrown){
                    loading_end();
                }
            })
        sign=setInterval(
            function(){
                $.ajax({
                    url:'/data/preview/realtime',
                    type:'get',
                    dataType:'text',
                    timeout: 1800,
                    data:{  'sel_device_id': $('#sel_device').children('option:selected').attr('value'),
                            'owner':$('#sel_chamber').children('option:selected').attr('value'),
                            'proj_type': 'carbon_dev',
                         },
                    success:function(data, status){
                        var data = $.parseJSON(data);
                        var current_date = data['date'];
                        var data_content = data['content'];
                        var owner = $('#sel_chamber').children('option:selected').attr('value');
                        if(data_content){
                            var innerHTML_str = '<colgroup><col class="col-xs-1"><col class="col-xs-3"></colgroup><thead><tr><th>项目</th><th>信息</th></tr></thead>';
                            chart_content_info = get_chart_content_info(owner);


                            for(var i =0; i<data_content.length;i++){
                                if(data_content[i]['owner'] == owner){
                                    for(var j = 0;j<chart_content_info.length;j++){
                                        var series_index = chart_content_info[j]['data_type_ids'].indexOf(data_content[i]['type_id'])
                                        if(series_index >= 0)
                                        {
                                            var chart = $('#'+chart_content_info[j]['container_id']).highcharts();
                                            var series = chart.series;
                                            serie_1_len = series[series_index].data.length;
                                            if(serie_1_len != 0){
                                            var plot_data = [current_date, data_content[i]['value']];
                                            if(series[series_index].data[serie_1_len-1]['x'] != plot_data[0]){
                                                if(plot_data[0]-series[series_index].data[0]['x']>=20*60*1000){
                                                    series[series_index].addPoint(plot_data,true,true)
                                                }
                                                else{
                                                    series[series_index].addPoint(plot_data,true,false)
                                                }
                                            }
                                        }
                                        }


                                    }
                                    var value = parseFloat(data_content[i]['value']);
                                    value = value.toFixed(2);
                                    innerHTML_str = innerHTML_str + '<tr>'+'<td>'+data_content[i]['name']+'</td>'+'<td>'+value+'</td>'+'</tr>'

                                }


                            }
                            document.getElementById('data_table').innerHTML = innerHTML_str;


                        }
                    }
                })
            },2000
        )
    }
}

var chart_info;

function get_chart_content_info(owner){
    return chart_info[owner];
}

function get_data_by_type_id(jdata, type_id){
    for(var i = 0;i<jdata.length;i++){
        if(jdata[i]['type_id']==type_id)
        {
            return jdata[i];
        }
    }
    return null;
}
$(function(){
    var opts = {
      lines: 12,            // The number of lines to draw
      length: 7,            // The length of each line
      width: 5,             // The line thickness
      radius: 10,           // The radius of the inner circle
      scale: 1.0,           // Scales overall size of the spinner
      corners: 1,           // Roundness (0..1)
      color: '#000',        // #rgb or #rrggbb
      opacity: 1/4,         // Opacity of the lines
      rotate: 0,            // Rotation offset
      direction: 1,         // 1: clockwise, -1: counterclockwise
      speed: 1,             // Rounds per second
      trail: 100,           // Afterglow percentage
      fps: 20,              // Frames per second when using setTimeout()
      zIndex: 2e9,          // Use a high z-index by default
      className: 'spinner', // CSS class to assign to the element
      top: '100px',           // center vertically
      left: '50%',          // center horizontally
      shadow: false,        // Whether to render a shadow
      hwaccel: false,       // Whether to use hardware acceleration (might be buggy)
      position: 'absolute'  // Element positioning
    };
    var target = document.getElementsByClassName('LoadingImg');
    //alert(target)
    //var spinner = new Spinner(opts).spin(target);
    var spinner = new Spinner().spin(target[0]);
    //$(function(){
    //    render_chart()
    //    });
    //load the conf file

    $.ajax({
        url:'/data/conf',
        type:'get',
        dataType:'text',
        timeout: 1800,
        data:{'proj_type': 'carbon_dev',
            'created_at': new Date()},
        success:function(data, status){
            var data = $.parseJSON(data);

            //add the option for select

            chart_info = data;
            on_selected_change();


        },
        notmodified:function(data, status){
            var data = $.parseJSON(data);

            //add the option for select

            chart_info = data;
            on_selected_change();
        }

    })



});


function loading_begin(loading_message){
    $(".LoadingBg").height(document.body.clientWidth);
    $(".LoadingBg").show();
    $(".LoadingImg").fadeIn(300);
    $(".Loading_message").html("<p>"+loading_message+"</p>");
    $(".Loading_message").fadeIn(300)

}
function loading_end(){
    $('.LoadingBg, .LoadingImg, .Loading_message').hide();
}




Date.prototype.pattern=function(fmt) {
    var o = {
    "M+" : this.getMonth()+1, //月份
    "d+" : this.getDate(), //日
    "h+" : this.getHours(), //小时
    "H+" : this.getHours(), //小时
    "m+" : this.getMinutes(), //分
    "s+" : this.getSeconds(), //秒
    "q+" : Math.floor((this.getMonth()+3)/3), //季度
    "S" : this.getMilliseconds() //毫秒
    };
    var week = {
    "0" : "/u65e5",
    "1" : "/u4e00",
    "2" : "/u4e8c",
    "3" : "/u4e09",
    "4" : "/u56db",
    "5" : "/u4e94",
    "6" : "/u516d"
    };
    if(/(y+)/.test(fmt)){
        fmt=fmt.replace(RegExp.$1, (this.getFullYear()+"").substr(4 - RegExp.$1.length));
    }
    if(/(E+)/.test(fmt)){
        fmt=fmt.replace(RegExp.$1, ((RegExp.$1.length>1) ? (RegExp.$1.length>2 ? "/u661f/u671f" : "/u5468") : "")+week[this.getDay()+""]);
    }
    for(var k in o){
        if(new RegExp("("+ k +")").test(fmt)){
            fmt = fmt.replace(RegExp.$1, (RegExp.$1.length==1) ? (o[k]) : (("00"+ o[k]).substr((""+ o[k]).length)));
        }
    }
    return fmt;
}
