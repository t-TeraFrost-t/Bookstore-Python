$(document).ready(()=>{
    $("#filter").hide()
    $("#fil").show()
    $('#fil').click(()=>{
        
            console.log('trip')     
            if($('#fil').val() == 1){
                $("#filter").show()
                $('#fil').val(0)
            }else{
                $("#filter").hide()
                $('#fil').val(1)
            }
    })
    $('.butt-book').click(()=>{
        console.log('rib');
        $.ajax({
            url: '/backoffice-books',
            type: 'GET',
            data: { 
                name: $('#name').val(),
                autor: $('#autor').val(),
                lower: $('#amountLower').val(),
                upper: $('#amountUpper').val(),
                gener: $('#gener').val(),
                page: $(event.currentTarget).val()
            },
            success: (data)=>{
                let newDoc = document.open("text/html", "replace");
                newDoc.write(data);
                newDoc.close();
            }
        });
    })
});