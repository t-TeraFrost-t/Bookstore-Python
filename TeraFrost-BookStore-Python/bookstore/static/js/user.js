$(document).ready(()=>{
    $('.button').click(()=>{
        console.log('rib');
        $.ajax({
            url: '/backoffice-users',
            type: 'GET',
            data: { 
                name: $('#name').val(),
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