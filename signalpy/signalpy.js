function SignalPy(url,secure){
    if (secure === undefined) {
    secure = '://';
    } 
    if (secure === true) {
    secure = 's://';
    } 
    if (secure === undefined) {
    secure = '://';
    }
    if ('WebSocket' in window){
        url='ws'+secure+url;
        w = new WebSocket(url);
        return w;
    }
    else{
        url='http'+secure+url;
        obj = new signalpyajax();
        obj.url=url;
        obj.receive();
        return obj;
    }
}
signalpyajax={
    id:"",
    url:"",
    onopen:function(){
        this.state='open'
    },
    onerror:function(obj){},
    onmessage:function(msg){},
    _open:function(msg){
        if(this.id===''){
            this.id=msg;this.onopen()
        }else{
            arr=JSON.parse(msg)
            for(message in arr){
                this.onmessage({data:message})
            }
        }
        this.receive();
    },
    receive:function () {
    _this=this;
    var request = this.return_ajax();
    request.open('POST',this.url+'?id='+this.id);
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            _this._open(this.responseText)
        }
    };
    request.onerror = function() {
        _this.onerror({})
    };
    request.send();
},
    send:function (msg) {
    _this=this;
    var request = this.return_ajax()
    request.open('POST',this.url+this.id);
    request.onerror = function() {
        _this.onerror({message:msg})
    };
    request.send(msg);
},

    return_ajax:function (){
    try{
        // Opera 8.0+, Firefox, Safari (1st attempt)
        xhttp = new XMLHttpRequest();
        return xhttp;
    }catch (e){
        // IE browser (2nd attempt)
        try{
            xhttp = new ActiveXObject("Msxml2.XMLHTTP");
            return xhttp;
        }catch (e) {
            try{
                // 3rd attempt
                xhttp = new ActiveXObject("Microsoft.XMLHTTP");
                return xhttp;
            }catch (e){
                return false;
        }
    }
}
    }}
