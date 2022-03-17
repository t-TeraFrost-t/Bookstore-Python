$(document).ready(()=>{
    $('.butt-order').click(()=>{
        console.log('rib');
        $.ajax({
            url: '/backoffice-orders',
            type: 'GET',
            data: { 
                name: $('#name').val(),
                upperPrice: $('#upperPrice').val(),
                lowerPrice: $('#lowerPrice').val(),
                upperDate: $('#upperDate').val(),
                lowerDate: $('#lowerDate').val(),
                status: $('status').val(),
                page: $(event.currentTarget).val()
            },
            success: (data)=>{
                let newDoc = document.open("text/html", "replace");
                newDoc.write(data);
                newDoc.close();
            }
        });
    })
    $('#add-book').click(()=>{
        var data = Array();
    
        $("table tr").each(function(i, v){
            data[i] = Array();
            $(this).children('td').each(function(ii, vv){
                data[i][ii] = $(this).text();
             }); 
         })
        console.log(data);
        for(let i=1;i<data.length-1;i++){
            if(data[i][0]===$('#isbn').val()){
                alert("you can't add this book again" );
                return;
             }
        }
        $('#tb').append(`<tr><td>${$('#isbn').val()}</td><td>${$('#price').val()}</td><td>${$('#amount').val()}</td></tr>`);
    })
    $('#add-order').click(()=>{
        var data = Array();
    
        $("table tr").each(function(i, v){
            data[i] = Array();
            $(this).children('td').each(function(ii, vv){
                data[i][ii] = $(this).text();
             }); 
         })
        let isbns = [];
        let prices = [];
        let amounts = [];
        for(let i=1;i<data.length-1;i++){
            isbns[i-1] = data[i][0];
            prices[i-1] = data[i][1];
            amounts[i-1] = data[i][2];
        }
        console.log(isbns,prices,amounts);
        if(isbns.length===0){
            alert('You can not Create an empthy order');
            return;
        }
        //console.log(prices);
        $.post('/add-order',{date:$('#date').val(),
                             user:$("#user").val(),
                             status:$('#status').val(),
                             isbns: isbns,
                             prices: prices,
                             amounts: amounts},(data)=>{
                                if(!alert(data)){window.location.href=`/backoffice-orders`;}
                             })
       
    })  
});