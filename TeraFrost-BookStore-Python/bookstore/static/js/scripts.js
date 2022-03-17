$(document).ready(()=>{
    console.log('hi');
    $('#status-modal').hide();
    $.get('/basket/size',(data)=>{
        console.log(data)
        $('#cart').text(data)
    })
    $("#order").click(()=>{

        $('#status-modal').show();  
    })
    
    $('#user').keyup(()=>{
        $('#user').attr(('list','suggestions-users'))
        $.get(`/sugestions/users/${$('#user').val()}`,(data)=>{
            //console.log(data);
            $('#suggestions-users').empty();
            data.forEach(element => {
                console.log(element);
                $('#suggestions-users').append(`<option>${element}</option>`)
            });
        })
    });
    $('#userShow').change(()=>{
        if($('#userShow').val()=='True'){
            $('#user').prop("disabled", false);
        }
        if($('#userShow').val()=='False'){
            $('#user').prop("disabled", true);
            $('#user').val('');
        }
    })
    $('#statusShow').change(()=>{
        if($('#statusShow').val()=='True'){
            $('#status').prop("disabled", false);
        }
        if($('#statusShow').val()=='False'){
            $('#status').prop("disabled", true);
            $('#status').val('');
        }
    })
    $('#paymentTypeShow').change(()=>{
        if($('#paymentTypeShow').val()=='True'){
            $('#paymentType').prop("disabled", false);
        }
        if($('#paymentTypeShow').val()=='False'){
            $('#paymentType').prop("disabled", true);
            $('#paymentType').val('');
        }
    })
    if($('#paymentTypeShow').val()=='True'){
        $('#paymentType').prop("disabled", false);
    }
    if($('#paymentTypeShow').val()=='False'){
        $('#paymentType').prop("disabled", true);
        $('#paymentType').val('');
    }
    if($('#statusShow').val()=='True'){
        $('#status').prop("disabled", false);
    }
    if($('#statusShow').val()=='False'){
        $('#status').prop("disabled", true);
        $('#status').val('');
    }
    if($('#userShow').val()=='True'){
        $('#user').prop("disabled", false);
    }
    if($('#userShow').val()=='False'){
        $('#user').prop("disabled", true);
        $('#user').val('');
    }
    $("input[type='checkbox']").change(function() {
        console.log('hi');
        if(this.checked) {
            $.ajax({
                url: '/add-permition',
                type: 'POST',
                data: { 
                    permition: $(event.currentTarget).val(),
                    role: $('#role').val()
                },
                success: (data)=>{
                    if(!alert(data)) window.location.href = `/permitions-role/${$('#role').val()}`;
                }
            });
        }else{
            $.ajax({
                url: '/remove-permition',
                type: 'POST',
                data: { 
                    permition: $(event.currentTarget).val(),
                    role: $('#role').val()
                },
                success: (data)=>{
                    if(!alert(data)) window.location.href = `/permitions-role/${$('#role').val()}`;
                }
            });
        }
    });
    $('#navbar-backoffice').ready(()=>{
        console.log('tri');
        $.ajax({
            url: '/permition-read',
            type: 'GET',
            success: (data)=>{
                console.log(data)
                $('#navbar-backoffice').append(data);
            }
        });
    })
});